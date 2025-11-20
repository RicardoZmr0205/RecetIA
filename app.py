from flask import Flask, render_template, request
from google import genai
import os 

app = Flask(__name__)


try:
    api_key = "AIzaSyAzRWRMGWO1QKuworJHMYVKvedmEoJ7578"
    if not api_key:
        
        raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
        
    client = genai.Client(api_key=api_key)
    
except Exception as e:
    
    print(f"ERROR DE CONFIGURACIÓN DE GEMINI: {e}")
    client = None 


def generar_receta_con_ia(ingredientes, region):
    """Genera una receta usando el modelo Gemini, solicitando formato HTML."""
    
    if not client:
        return "❌ ERROR: El servicio de IA no está configurado (revisa tu clave API)."
        
   
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
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
       
        return response.text

    except Exception as e:
        return f"❌ ERROR al conectar con la IA: {e}"




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
 
        ingredientes = request.form.get('ingredientes')
        region = request.form.get('region')

        if not ingredientes or not region:
            mensaje = "🚫 **Error de Formulario:** Por favor, ingresa tus **ingredientes** y selecciona una **región** (Costa, Sierra o Selva) para continuar."
            return render_template('resultado.html', resultado=mensaje), 400

        resultado_ia = generar_receta_con_ia(ingredientes, region)
        
        return render_template('resultado.html', resultado=resultado_ia)

    except Exception as e:
        return render_template('resultado.html', resultado=f"Ocurrió un error inesperado en el servidor: {e}"), 500


if __name__ == '__main__':
    
    print("\n--- Ejecutando RecetIA ---")
    print("Asegúrate de que la variable GEMINI_API_KEY esté configurada.")

#    app.run(debug=True)

