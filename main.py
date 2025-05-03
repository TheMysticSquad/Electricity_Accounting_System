from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.image import Image
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# PostgreSQL connection (replace with your credentials)
DB_URL = "postgresql://neondb_owner:npg_OqnZp0BDwSE1@ep-shy-poetry-abbw3imb-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

# KV Layout
KV = '''
ScreenManager:
    LoginScreen:
    MenuScreen:
    DashboardScreen:

<LoginScreen>:
    name: 'login'

    MDBoxLayout:
        orientation: 'vertical'
        spacing: 20
        padding: 50

        MDLabel:
            text: "Energy Login"
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: 0, 0, 0, 1
            font_style: 'H4'

        MDTextField:
            id: username
            hint_text: "Username"

        MDTextField:
            id: password
            hint_text: "Password"
            password: True

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            on_release: root.validate_user()

<MenuScreen>:
    name: 'menu'

    MDBoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 30

        MDLabel:
            text: "Reports"
            halign: "center"
            font_style: "H4"

        MDRaisedButton:
            text: "General Report"
            pos_hint: {"center_x": 0.5}
            on_release:
                app.root.current = 'dashboard'

        MDRaisedButton:
            text: "Other Report (Coming Soon)"
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "Logout"
            pos_hint: {"center_x": 0.5}
            on_release:
                app.root.current = 'login'

<DashboardScreen>:
    name: 'dashboard'

    MDBoxLayout:
        orientation: 'vertical'
        spacing: 10

        MDLabel:
            text: "General Energy Report"
            halign: "center"
            font_style: "H5"
            size_hint_y: 0.1

        BoxLayout:
            id: chart_area
            orientation: 'vertical'
            size_hint_y: 0.9
            padding: 10
            spacing: 10           
              

        MDRaisedButton:
            text: "Back to Menu"
            pos_hint: {"center_x": 0.5}
            on_release:
                app.root.current = 'menu'
'''

class LoginScreen(MDScreen):
    def validate_user(self):
        user = self.ids.username.text
        pwd = self.ids.password.text
        if user == "admin" and pwd == "1234":
            self.manager.current = "menu"
        else:
            self.ids.username.error = True
            self.ids.password.error = True

class MenuScreen(MDScreen):
    pass

class DashboardScreen(MDScreen):
    def on_enter(self):
        self.ids.chart_area.clear_widgets()
        try:
            df = self.get_energy_data()
            fig, axs = plt.subplots(2, 1, figsize=(6, 8))

            # Bar Chart
            df.groupby('district_name')['substation_consumer_count'].sum().plot(kind='bar', ax=axs[0], color='skyblue')
            axs[0].set_title("Total Consumer by Substation")

            axs[0].set_xlabel("Feeder ID")
            axs[0].set_ylabel("Total Consumption (kVA)")
            axs[0].grid()


            self.ids.chart_area.add_widget(FigureCanvasKivyAgg(fig))
        except Exception as e:
            self.ids.chart_area.add_widget(MDLabel(text=str(e), halign="center"))

    def get_energy_data(self):
        with psycopg2.connect(DB_URL) as conn:
            query = """
                WITH consumer_metrics AS (
                    SELECT
                        dtr_id,
                        COUNT(consumer_no) AS consumer_count,
                        SUM(load_kw) AS total_load_kw
                    FROM public.consumers
                    GROUP BY dtr_id
                ),
                dtr_with_metrics AS (
                    SELECT
                        dtrs.id AS dtr_id,
                        dtrs.name AS dtr_name,
                        dtrs.feeder_id,
                        consumer_metrics.consumer_count,
                        consumer_metrics.total_load_kw
                    FROM public.dtrs
                    LEFT JOIN consumer_metrics ON dtrs.id = consumer_metrics.dtr_id
                ),
                feeder_with_metrics AS (
                    SELECT
                        feeders.id AS feeder_id,
                        feeders.name AS feeder_name,
                        feeders.substation_id,
                        COALESCE(SUM(dtr_with_metrics.consumer_count), 0) AS consumer_count,
                        COALESCE(SUM(dtr_with_metrics.total_load_kw), 0) AS total_load_kw
                    FROM public.feeders
                    LEFT JOIN dtr_with_metrics ON feeders.id = dtr_with_metrics.feeder_id
                    GROUP BY feeders.id, feeders.name, feeders.substation_id
                ),
                substation_with_metrics AS (
                    SELECT
                        substations.id AS substation_id,
                        substations.name AS substation_name,
                        substations.district_id,
                        COALESCE(SUM(feeder_with_metrics.consumer_count), 0) AS consumer_count,
                        COALESCE(SUM(feeder_with_metrics.total_load_kw), 0) AS total_load_kw
                    FROM public.substations
                    LEFT JOIN feeder_with_metrics ON substations.id = feeder_with_metrics.substation_id
                    GROUP BY substations.id, substations.name, substations.district_id
                )
                SELECT
                    districts.name AS district_name,
                    substations.name AS substation_name,
                    feeders.name AS feeder_name,
                    dtrs.name AS dtr_name,

                    COALESCE(consumer_metrics.consumer_count, 0) AS dtr_consumer_count,
                    COALESCE(consumer_metrics.total_load_kw, 0) AS dtr_total_load_kw,

                    COALESCE(feeder_with_metrics.consumer_count, 0) AS feeder_consumer_count,
                    COALESCE(feeder_with_metrics.total_load_kw, 0) AS feeder_total_load_kw,

                    COALESCE(substation_with_metrics.consumer_count, 0) AS substation_consumer_count,
                    COALESCE(substation_with_metrics.total_load_kw, 0) AS substation_total_load_kw
                FROM public.dtrs
                LEFT JOIN consumer_metrics ON dtrs.id = consumer_metrics.dtr_id
                LEFT JOIN public.feeders ON dtrs.feeder_id = feeders.id
                LEFT JOIN feeder_with_metrics ON feeders.id = feeder_with_metrics.feeder_id
                LEFT JOIN public.substations ON feeders.substation_id = substations.id
                LEFT JOIN substation_with_metrics ON substations.id = substation_with_metrics.substation_id
                LEFT JOIN public.districts ON substations.district_id = districts.id
                ORDER BY district_name, substation_name, feeder_name, dtr_name;
            """
            df = pd.read_sql(query, conn)
        return df

class EnergyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    EnergyApp().run()
