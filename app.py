from flask import Flask, render_template, request
from google import genai
import os # Importamos 'os' para manejar la variable de entorno

# =================================================================
# CONFIGURACIÓN DE FLASK Y GEMINI
# =================================================================

app = Flask(__name__)

# Configuración del cliente Gemini
try:
    # Intenta obtener la clave API de la variable de entorno
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Si la clave no está en el entorno, lanza una advertencia
        raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
        
    client = genai.Client(api_key=api_key)
    
except Exception as e:
    # Manejo de error si la clave API no está disponible
    print(f"ERROR DE CONFIGURACIÓN DE GEMINI: {e}")
    client = None # El cliente será None si hay un error

# =================================================================
# FUNCIÓN CENTRAL: LLAMADA A LA IA
# =================================================================

def generar_receta_con_ia(ingredientes, region):
    """Genera una receta usando el modelo Gemini, solicitando formato HTML."""
    
    if not client:
        return "❌ ERROR: El servicio de IA no está configurado (revisa tu clave API)."
        
    # Construcción del prompt (instrucción detallada para el modelo)
    prompt = f"""
    Eres RecetIA, un asistente culinario experto en gastronomía peruana.
    Tu tarea es crear una **única receta tradicional peruana** que utilice los ingredientes disponibles
    y esté adaptada a la región indicada.

    **FORMATO DE SALIDA ESTRICTO:**
    Genera el contenido utilizando **solamente etiquetas HTML** para la estructura, sin usar Markdown.
    Usa etiquetas como <h1>, <b>, <p>, <br> y <ul> con <li>.

    **Estructura requerida (en HTML):**
    1.  Utiliza la etiqueta **<h1>** para el Título de la Receta.
    2.  Utiliza una etiqueta **<p>** para la Descripción breve.
    3.  Para la sección de Ingredientes, usa **<b>Ingredientes:</b><br>** seguido de una lista no ordenada **<ul>** con elementos **<li>**.
    4.  Para las Instrucciones, usa **<b>Instrucciones de Preparación:</b><br>** seguido de una lista ordenada **<ol>** con elementos **<li>**.
    5.  Asegúrate de que el plato sea de la cocina peruana, enfocándote en las particularidades de la región {region.upper()}.

    **Datos del usuario:**
    - Ingredientes disponibles: {ingredientes}
    - Región de enfoque: {region.upper()}
    """

    try:
        # Llamada a la API de Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # El resultado ahora debería contener etiquetas HTML para el formato
        return response.text

    except Exception as e:
        return f"❌ ERROR al conectar con la IA: {e}"


# =================================================================
# RUTAS DE FLASK
# =================================================================

@app.route('/', methods=['GET'])
def index():
    """Ruta para la página principal, renderiza index.html."""
    return render_template('index.html')


@app.route('/recetas', methods=['POST'])
def buscar_recetas():
    """
    Recibe los datos del formulario, valida y llama a la IA para generar la receta.
    """
    try:
        # 1. Obtener datos del formulario
        ingredientes = request.form.get('ingredientes')
        region = request.form.get('region')

        # 2. **VALIDACIÓN REQUERIDA**
        if not ingredientes or not region:
            mensaje = "🚫 **Error de Formulario:** Por favor, ingresa tus **ingredientes** y selecciona una **región** (Costa, Sierra o Selva) para continuar."
            return render_template('resultado.html', resultado=mensaje), 400

        # 3. Llamada a la función de la IA
        resultado_ia = generar_receta_con_ia(ingredientes, region)
        
        # 4. Renderiza la página de resultados
        return render_template('resultado.html', resultado=resultado_ia)

    except Exception as e:
        return render_template('resultado.html', resultado=f"Ocurrió un error inesperado en el servidor: {e}"), 500


# =================================================================
# INICIO DE LA APLICACIÓN
# =================================================================
if __name__ == '__main__':
    # Asegúrate de que tu clave API esté configurada antes de ejecutar
    print("\n--- Ejecutando RecetIA ---")
    print("Asegúrate de que la variable GEMINI_API_KEY esté configurada.")

    app.run(debug=True)
