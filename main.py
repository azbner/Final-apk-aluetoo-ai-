import flet as ft
from groq import Groq
from datetime import datetime
import pytz
import base64

# --- CONFIGURATION ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def main(page: ft.Page):
    # Configuration de la page (Le "set_page_config" de Flet)
    page.title = "ALUETOO AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b0e14"
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- ÉLÉMENTS DE L'INTERFACE ---
    
    # Titre Style XXL
    title = ft.ShaderMask(
        content=ft.Text("ALUETOO AI", size=50, weight=ft.FontWeight.BOLD),
        blend_mode=ft.BlendMode.SRC_IN,
        shader=ft.LinearGradient(
            colors=["#ff4b4b", "#af40ff", "#00d4ff"],
        ),
    )

    # Sous-titre avec l'heure
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    salut = "Bonjour" if 5 <= now.hour < 18 else "Bonsoir"
    sub_title = ft.Text(
        f"{salut} ! Nous sommes le {now.strftime('%d/%m/%Y')}, il est {now.strftime('%H:%M')}.",
        size=16, color="#e6edf3", opacity=0.8
    )

    # Historique des messages (La zone de chat)
    chat_history = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=10)

    # Fonction pour envoyer un message
    def send_message(e):
        if not user_input.value:
            return
        
        user_text = user_input.value
        user_input.value = ""
        
        # Ajouter le message utilisateur à l'écran
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(user_text, size=18, color="white"),
                bgcolor="#161b22", padding=15, border_radius=15, alignment=ft.alignment.center_right
            )
        )
        page.update()

        # Appel à Groq (IA)
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es ALUETOO AI, créée par Léo Ciach. Élégante et intelligente."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_response = completion.choices[0].message.content
            
            # Ajouter la réponse de l'IA
            chat_history.controls.append(
                ft.Container(
                    content=ft.Text(ai_response, size=18, color="#e6edf3"),
                    gradient=ft.LinearGradient(colors=["#af40ff", "#00d4ff"]),
                    padding=15, border_radius=15
                )
            )
        except Exception as ex:
            chat_history.controls.append(ft.Text(f"Erreur : {ex}", color="red"))
        
        page.update()

    # Barre d'entrée (Le chat_input)
    user_input = ft.TextField(
        hint_text="Dis quelque chose à ALUETOO...",
        border_radius=30,
        border_color="#af40ff",
        bgcolor="#161b22",
        expand=True,
        on_submit=send_message
    )

    # --- MISE EN PAGE FINALE ---
    page.add(
        ft.Column(
            [
                ft.Center(title),
                ft.Center(sub_title),
                ft.Divider(height=20, color="transparent"),
                ft.Container(content=chat_history, height=450), # Zone de chat
                ft.Row(
                    [
                        user_input,
                        ft.FloatingActionButton(icon=ft.icons.SEND, on_click=send_message, bgcolor="#af40ff")
                    ]
                )
            ],
            expand=True
        )
    )
    page.update()

ft.app(target=main)
