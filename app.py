from flask import Flask, request, abort
from twilio.twiml.messaging_response import MessagingResponse
import random
import re
import os
import json

app = Flask(__name__)

EBOOK_PATH = os.getenv("EBOOK_PATH", "./Ebook.txt")

FRASES_MOTIVACIONALES = [
    "💡 Recuerda: La comunicación efectiva es la clave del éxito.",
    "🚀 Cada paso que das te acerca a tu meta.",
    "✨ ¡Tu historia merece ser contada con impacto!"
]

DATOS_INTERESANTES = {
    "ventas": "📈 Tip de Ventas: Escucha más de lo que hablas.",
    "clientes": "🎯 Fidelización: Un cliente feliz te recomienda gratis.",
    "marketing": "📣 Usa testimonios reales en redes.",
    "productividad": "⏳ Técnica Pomodoro: 25 min enfoque + 5 descanso."
}

DATOS_RANDOM_INICIO = [
    "El 70% del cuerpo es agua",
    "Beber agua mejora la concentración",
    "Cuidar tu salud previene gastos mayores"
]

def es_correo_valido(email):
    return re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]{2,}$", email)

def limpiar_telefono(texto):
    return re.sub(r"[^0-9]", "", texto)

usuarios = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.values.get('From', '')
    body = request.values.get('Body', '').strip().lower()

    if from_number not in usuarios:
        usuarios[from_number] = {"estado": "INICIO"}

    estado = usuarios[from_number]["estado"]
    resp = MessagingResponse()
    msg = resp.message()

    if estado == "INICIO":
        if body == "join education-appearance":
            dato = random.choice(DATOS_RANDOM_INICIO)
            usuarios[from_number]["estado"] = "PREGUNTA_NOMBRE"
            msg.body(f"¡Hola! Soy ÑecoBot 🤖\n{dato}\n\n¿Quieres un ebook gratis? Responde 'sí' o 'no'.")
        else:
            msg.body("Envía: join education-appearance para empezar.")
    elif estado == "PREGUNTA_NOMBRE":
        if body in ["sí", "si", "s"]:
            usuarios[from_number]["estado"] = "PIDE_NOMBRE"
            msg.body("📚 ¡Genial! ¿Cuál es tu nombre?")
        elif body in ["no", "n"]:
            usuarios[from_number]["estado"] = "FIN"
            msg.body("👌 Entiendo. ¡Aquí estaré si cambias de opinión!")
        else:
            msg.body("Responde 'sí' o 'no' para continuar.")
    elif estado == "PIDE_NOMBRE":
        usuarios[from_number]["nombre"] = body.title()
        usuarios[from_number]["estado"] = "PIDE_EMAIL"
        msg.body(f"Mucho gusto, {usuarios[from_number]['nombre']} 🙌 ¿Tu correo electrónico?")
    elif estado == "PIDE_EMAIL":
        if not es_correo_valido(body):
            msg.body("❗ El correo no es válido. Intenta de nuevo.")
        else:
            usuarios[from_number]["email"] = body
            usuarios[from_number]["estado"] = "PIDE_TELEFONO"
            msg.body("📱 Ahora tu teléfono (10 dígitos):")
    elif estado == "PIDE_TELEFONO":
        tel = limpiar_telefono(body)
        if len(tel) != 10:
            msg.body("📵 Debe tener 10 dígitos. Intenta de nuevo.")
        else:
            usuarios[from_number]["telefono"] = tel
            usuarios[from_number]["estado"] = "PIDE_CIUDAD"
            msg.body("📍 ¿En qué ciudad estás?")
    elif estado == "PIDE_CIUDAD":
        usuarios[from_number]["ciudad"] = body.title()
        usuarios[from_number]["estado"] = "PIDE_GIRO"
        msg.body("🏢 ¿A qué se dedica tu negocio?")
    elif estado == "PIDE_GIRO":
        usuarios[from_number]["giro"] = body.title()
        usuarios[from_number]["estado"] = "PIDE_REFERENCIA"
        msg.body("🔗 ¿Dónde nos encontraste? (Facebook, recomendación, etc.)")
    elif estado == "PIDE_REFERENCIA":
        usuarios[from_number]["referencia"] = body.title()
        if os.path.exists(EBOOK_PATH):
            with open(EBOOK_PATH, "r", encoding="utf-8") as f:
                ebook = f.read()
            msg.body(f"📖 Aquí está tu ebook:\n\n{ebook}\n\n¡Gracias por unirte!")
        else:
            msg.body("⚠️ No encontré el ebook. Contacta a soporte.")
        usuarios[from_number]["estado"] = "FIN"
    else:
        msg.body("Gracias por tu tiempo. ¡Mucho éxito! 🙌")

    return str(resp)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
