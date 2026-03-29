import flet as ft
from groq import Groq
import base64
import os
from datetime import datetime
import pytz

# --- CONFIGURATION GROQ ---
# Remplace par ta clé ou configure une variable d'environnement
GROQ_API_KEY = "TA_CLE_GROQ_ICI" 
client = Groq(api_key=GROQ_API_KEY)

def main(page: ft.Page):
    # Configuration de la page (Mode Mobile)
    page.title = "ALUETOO AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b0e14"
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Historique des messages
    chat_history = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=20)
    
    # Variable pour stocker l'image encodée
    current_image_base64 = [None]

    # --- FONCTIONS ---
    def get_time_greeting():
        tz = pytz.timezone('Europe/Paris')
        now = datetime.now(tz)
        salut = "Bonjour" if 5 <= now.hour < 18 else "Bonsoir"
        return f"{salut} ! Il est {now.strftime('%H:%M')}."

    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            with open(file.path, "rb") as f:
                current_image_base64[0] = base64.b64encode(f.read()).decode('utf-8')
            snack = ft.SnackBar(ft.Text("📸 Image prête pour analyse !"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    def send_message(e):
        if not chat_input.value and not current_image_base64[0]:
            return

        user_text = chat_input.value
        chat_input.value = ""
        
        # Affichage message utilisateur
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(user_text, size=18, color="white"),
                bgcolor="#161b22",
                padding=15,
                border_radius=15,
                alignment=ft.alignment.center_right
            )
        )
        page.update()

        try:
            # Choix du modèle (Llama 4 pour la vision si image présente)
            if current_image_base64[0]:
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
                content = [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{current_image_base64[0]}"}}
                ]
            else:
                model = "llama-3.3-70b-versatile"
                content = user_text

            # Appel API Groq
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}],
            )
            
            bot_response = response.choices[0].message.content
            
            # Affichage réponse AI
            chat_history.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(bot_response, size=18, color="#e6edf3"),
                        ft.IconButton(
                            icon=ft.icons.VOLUME_UP, 
                            icon_color="#af40ff",
                            on_click=lambda _: page.tts.speak(bot_response)
                        )
                    ]),
                    padding=15,
                    border_radius=15,
                )
            )
            current_image_base64[0] = None # Reset image après envoi
            page.update()

        except Exception as ex:
            chat_history.controls.append(ft.Text(f"Erreur : {ex}", color="red"))
            page.update()

    # --- INTERFACE (UI) ---
    page.tts = ft.TextToSpeech() # Moteur vocal intégré

    title = ft.ShaderMask(
        content=ft.Text("ALUETOO AI", size=50, weight="bold"),
        shader=ft.LinearGradient(["#ff4b4b", "#af40ff", "#00d4ff"]),
    )

    chat_input = ft.TextField(
        hint_text="Dis quelque chose...",
        border_radius=30,
        border_color="#af40ff",
        expand=True,
        on_submit=send_message
    )

    page.add(
        ft.Column([
            ft.Center(title),
            ft.Center(ft.Text(get_time_greeting(), size=16, color="grey")),
            ft.Divider(height=20, color="transparent"),
        ]),
        chat_history,
        ft.Row([
            ft.IconButton(ft.icons.ADD_A_PHOTO, on_click=lambda _: file_picker.pick_files()),
            chat_input,
            ft.IconButton(ft.icons.SEND, icon_color="#00d4ff", on_click=send_message),
        ])
    )

ft.app(target=main)
