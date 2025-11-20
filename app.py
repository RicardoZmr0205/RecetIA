from flask import Flask, json, render_template, request
from google import genai
import os 

app = Flask(__name__)


# --- CONFIGURACIÓN DE GEMINI ---
try:
    # ADVERTENCIA DE SEGURIDAD: Se recomienda encarecidamente usar os.getenv("GEMINI_API_KEY") 
    # y configurar la clave como una variable de entorno, no codificada.
    api_key = os.environ.get("GEMINI_API_KEY") 
    if not api_key:
        
        raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
        
    client = genai.Client(api_key=api_key)
    
except Exception as e:
    
    print(f"ERROR DE CONFIGURACIÓN DE GEMINI: {e}")
    client = None 


# --- FUNCIONES DE INTERACCIÓN CON LA IA ---

# FUNCIÓN 1: Genera un menú de 5 platos en formato JSON
def generar_menu_con_ia(ingredientes, region):
    """Genera una lista de 5 títulos de recetas con la IA, solicitando formato JSON."""
    if not client:
        return json.dumps({"recetas": [], "error": "❌ ERROR: El servicio de IA no está configurado."})
        
    prompt = f"""
    Eres RecetIA, un asistente culinario experto.
    Tu tarea es crear una lista de **5 títulos de platos peruanos** que utilicen los ingredientes disponibles
    y estén adaptados a la región indicada.

    **FORMATO DE SALIDA ESTRICTO:**
    Genera el contenido utilizando **solamente formato JSON**.
    El JSON debe ser un array llamado "recetas". Cada objeto en el array debe tener las claves: "titulo" y "descripcion_corta".

    **Estructura JSON requerida:**
    {{
        "recetas": [
            {{
                "titulo": "Título de la Receta 1",
                "descripcion_corta": "Breve descripción..."
            }},
            // ... 4 recetas más ...
        ]
    }}

    **Datos del usuario:**
    - Ingredientes disponibles: {ingredientes}
    - Región de enfoque: {region.upper()}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text 
    
    except Exception as e:
        return json.dumps({"recetas": [], "error": f"❌ ERROR al conectar con la IA: {e}"})

# FUNCIÓN 2: Genera la receta detallada en formato HTML
def generar_detalle_receta_con_ia(titulo, region):
    """Genera la receta completa para el título seleccionado, solicitando formato HTML."""
    if not client:
        return "❌ ERROR: El servicio de IA no está configurado (revisa tu clave API)."
        
    prompt = f"""
    Eres RecetIA. Tu tarea es generar la receta completa para el siguiente plato.

    **FORMATO DE SALIDA ESTRICTO:**
    Genera el contenido utilizando **solamente etiquetas HTML** para la estructura, sin usar Markdown.
    Usa etiquetas como <h1>, <b>, <p>, <br> y <ul>/<li> y <ol>/<li>.

    **Plato Solicitado:** {titulo}
    **Región de Enfoque:** {region.upper()}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text

    except Exception as e:
        return f"❌ ERROR al conectar con la IA: {e}"


# --- RUTAS DE LA APLICACIÓN ---

# RUTA 1: RUTA DE INICIO (Soluciona el error 404)
@app.route('/', methods=['GET'])
def index():
    """Ruta para la página principal, renderiza index.html."""
    return render_template('index.html')


# RUTA 2: BUSCAR MENÚ DE RECETAS (Recibe el formulario y muestra la lista de opciones)
@app.route('/recetas', methods=['POST'])
def buscar_menu():
    try:
        ingredientes = request.form.get('ingredientes')
        region = request.form.get('region')

        if not ingredientes or not region:
            mensaje = "🚫 **Error de Formulario:** Por favor, ingresa tus **ingredientes** y selecciona una **región**."
            return render_template('resultado.html', resultado=mensaje), 400

        # Llama a la IA para generar el menú JSON
        json_recetas = generar_menu_con_ia(ingredientes, region)
        
        # Intenta parsear el resultado JSON
        try:
            # Limpieza: Quitamos cualquier texto o marcador de formato (como ```json) que la IA pueda haber añadido
            json_recetas = json_recetas.strip()
            if json_recetas.startswith('```json'):
                json_recetas = json_recetas.replace('```json', '', 1).strip()
            if json_recetas.endswith('```'):
                json_recetas = json_recetas.rstrip('```').strip()
                
            data = json.loads(json_recetas)
            lista_recetas = data.get('recetas', [])
            
            if not lista_recetas:
                mensaje = "❌ ERROR: La IA no pudo generar recetas válidas. Inténtalo de nuevo con otros ingredientes."
                return render_template('resultado.html', resultado=mensaje), 500

        except json.JSONDecodeError:
            # Si falla el parseo (es decir, la IA no devolvió JSON limpio)
            mensaje = f"❌ ERROR: La IA no devolvió un formato de menú legible. Texto crudo devuelto: <pre>{json_recetas}</pre>"
            return render_template('resultado.html', resultado=mensaje), 500
        
        # Renderiza la nueva plantilla de menú (menu.html)
        return render_template('menu.html', recetas=lista_recetas, region=region, ingredientes=ingredientes)

    except Exception as e:
        return render_template('resultado.html', resultado=f"Ocurrió un error inesperado en el servidor: {e}"), 500


# RUTA 3: DETALLE DE RECETA (Recibe la selección del menú y muestra el detalle)
@app.route('/detalle_receta', methods=['POST'])
def mostrar_detalle():
    try:
        titulo = request.form.get('titulo')
        region = request.form.get('region')
        
        if not titulo or not region:
            mensaje = "🚫 **Error:** No se especificó el plato o la región."
            return render_template('resultado.html', resultado=mensaje), 400
            
        # Llama a la IA para generar el detalle en HTML
        resultado_ia = generar_detalle_receta_con_ia(titulo, region)
        
        # Renderiza el resultado con la plantilla que ya tienes (resultado.html)
        return render_template('resultado.html', resultado=resultado_ia)

    except Exception as e:
        return render_template('resultado.html', resultado=f"Ocurrió un error inesperado en el servidor: {e}"), 500


if __name__ == '__main__':
    
    print("\n--- Ejecutando RecetIA ---")
    print("Asegúrate de que la variable GEMINI_API_KEY esté configurada o la clave codificada es válida.")
    app.run(debug=True)