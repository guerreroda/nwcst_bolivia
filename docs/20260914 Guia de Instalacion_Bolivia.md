# Guía de instalación

**Herramientas para el Nowcasting del Crecimiento del PIB**
Banco Central de Bolivia · BID · septiembre–octubre de 2026

---

Esta guía deja su computadora lista para el curso. Toma entre **30 y 60 minutos**, casi
todo tiempo de espera mientras se descargan los programas.

**Hágalo antes de su clínica de instalación.** Si algo falla, no siga intentando: anote en
qué paso se detuvo y llévelo a la clínica. Ese es exactamente el propósito de la sesión.

**Lo que necesita antes de empezar**

| | |
|---|---|
| Sistema operativo | Windows 10 u 11, macOS 12 o superior, o Linux |
| Espacio en disco | 10 GB libres |
| Permisos | Poder instalar programas. En una computadora institucional esto suele requerir al área de sistemas: **pídalo hoy**, no el día de la clínica |
| Conexión | Estable durante la instalación; se descargan cerca de 3 GB |

---

## Paso 1. Instalar Anaconda

Anaconda trae Python y el administrador de entornos que usaremos todo el curso.

1. Vaya a `https://www.anaconda.com/download` y descargue el instalador de su sistema.
2. Ejecútelo y acepte todas las opciones por omisión.
3. En Windows, **no** marque la casilla "Add Anaconda to my PATH". Se trabajará desde el
   Anaconda Prompt, que el instalador agrega al menú de inicio.

**Para comprobarlo.** Abra el **Anaconda Prompt** (Windows) o la **Terminal** (macOS y
Linux) y escriba:

```
conda --version
```

Debe responder algo como `conda 24.9.2`. Si responde que el comando no existe, la
instalación no terminó: repórtelo en la clínica.

> Todo lo que sigue se escribe en esa misma ventana. Cada vez que esta guía muestre un
> bloque de texto en gris, se copia tal cual y se presiona Enter.

---

## Paso 2. Instalar Git

Git es lo que mantiene sincronizado el material del curso. Cuando el instructor corrija un
cuaderno, usted lo recibe con un solo comando en vez de volver a bajar una carpeta entera.

- **Windows:** descargue de `https://git-scm.com/download/win` y acepte las opciones por
  omisión.
- **macOS:** escriba `git --version` en la Terminal. Si no lo tiene, el sistema le ofrecerá
  instalarlo solo; acepte.
- **Linux:** `sudo apt install git` (Ubuntu y Debian) o `sudo dnf install git` (Fedora).

**Para comprobarlo:**

```
git --version
```

---

## Paso 3. Bajar el material del curso

Escriba, uno por uno:

```
cd %USERPROFILE%
git clone https://github.com/guerreroda/nwcst_bol.git
cd nwcst_bol
```

En macOS y Linux, el primer comando es `cd ~` en lugar de `cd %USERPROFILE%`.

> **El repositorio es privado.** Git le va a pedir usuario y contraseña de GitHub. Si
> todavía no tiene acceso, escriba al instructor con su nombre de usuario de GitHub **antes
> de la clínica**; dar el acceso toma un minuto, pero no se puede hacer si usted no tiene
> cuenta.

Al terminar, debe ver carpetas llamadas `code`, `docs`, `data`, `raw` y `output`.

---

## Paso 4. Crear el entorno del curso

Un *entorno* es una instalación de Python separada, con las versiones exactas que el curso
necesita y sin tocar nada más de su computadora. Si algo se rompe, se borra el entorno y se
vuelve a crear; no hay que reinstalar Anaconda.

```
cd code
conda env create -f environment.yml
```

**Esto tarda entre 10 y 20 minutos.** Es normal que se quede largo rato en la línea
`Solving environment`. Déjelo correr.

Si pasa de 20 minutos sin avanzar, deténgalo con Ctrl+C y use el resolvedor rápido:

```
conda install -n base mamba
mamba env create -f environment.yml
```

Si aun así falla, no insista con ese comando: en la carpeta `code` está
**`instalacion_manual.txt`**, que instala exactamente los mismos paquetes en varios pasos.
Sirve para ver **cuál** es el paquete que da problema, que es el dato que hace falta llevar
a la clínica.

Cuando termine, active el entorno:

```
conda activate nwcst
```

El nombre `(nwcst)` debe aparecer al inicio de la línea. **Hay que escribir `conda activate
nwcst` cada vez que se abre una ventana nueva**, todo el curso.

---

## Paso 5. Verificar

Este es el paso que importa. Desde la carpeta `code`, con el entorno activo:

```
python verificar_entorno.py
```

El programa imprime una línea por revisión y termina con un veredicto:

- **"la computadora está lista para el curso"** — terminó. Puede cerrar la ventana.
- **"faltan N cosas obligatorias"** — no siga adelante por su cuenta. Tome una captura de
  pantalla completa y llévela a la clínica.

Los renglones marcados `AVISO` no impiden empezar. El más común es que las llaves de
`config.py` todavía estén vacías, lo cual se resuelve en el paso 6.

---

## Paso 6. Llaves de acceso a los datos

Dos fuentes del curso piden una credencial gratuita. **Son personales: no se comparten ni
se suben a GitHub.**

### FRED (Reserva Federal de St. Louis)

Da las series internacionales que sirven de control: precios de materias primas, actividad
de los socios comerciales.

1. Cree una cuenta en `https://fredaccount.stlouisfed.org/apikeys`.
2. Pida una API key. Llega al instante; son 32 caracteres.

### NASA LAADS — **solo si va a trabajar luces nocturnas**

1. Cree una cuenta en `https://ladsweb.modaps.eosdis.nasa.gov`.
2. Entre a *My Account* → *Generate Token*.
3. **El token vence.** Si más adelante la descarga falla con un error de autorización, casi
   siempre es eso: genere uno nuevo.

### Dónde se guardan

Ambas van en **`code/config.py`**, que es el único archivo que se edita en este curso. Busque
estas dos líneas cerca del inicio y pegue sus valores entre las comillas:

```python
FRED_API_KEY = "escriba aqui su llave de FRED"
NASA_TOKEN   = "escriba aqui su token de NASA"
```

> **Tenga presente que `config.py` se versiona con git.** Lo que pegue ahí queda en el
> historial del repositorio, que es privado pero compartido con el resto del curso. Son
> credenciales personales de descarga, sin costo y revocables, así que el riesgo es bajo;
> aun así, no reutilice una contraseña ni pegue ahí ninguna otra credencial.

Vuelva a correr `python verificar_entorno.py`. Los avisos sobre las llaves deben
desaparecer.

---

## Paso 7 (opcional). Entorno de luces nocturnas

Solo para quien vaya a procesar imágenes satelitales VIIRS. **Si no es su caso, sáltelo**:
puede crearlo después sin problema.

```
conda env create -f environment-geo.yml
conda activate geo
python verificar_entorno.py --geo
```

Va en un entorno aparte a propósito: las librerías geográficas (GDAL, PROJ, rasterio) entran
en conflicto con las de modelos si comparten entorno.

Advertencia de tamaño: Bolivia es grande y mediterránea, así que su territorio cubre **cuatro
mosaicos VIIRS** frente a uno solo en los países del Caribe. La descarga pesa cuatro veces
más. Conviene dejarla corriendo fuera del horario de clase.

---

## Problemas frecuentes

**`conda` no es un comando reconocido (Windows).**
Está en la ventana equivocada. Use el **Anaconda Prompt** del menú de inicio, no el Símbolo
del sistema ni PowerShell.

**`conda env create` se queda pegado en "Solving environment".**
Espere 20 minutos. Si no avanza, use `mamba` como se indica en el paso 4, y si tampoco,
`code/instalacion_manual.txt`.

**`git clone` pide contraseña y la rechaza.**
GitHub ya no acepta la contraseña de la cuenta por línea de comandos. Hay que usar un
*personal access token* como contraseña, o instalar GitHub Desktop. Se resuelve en la
clínica.

**Error al importar `pmdarima` o `torch`.**
Casi siempre es numpy 2.x, que rompe la compatibilidad. El archivo `environment.yml` fija
`numpy=1.26.4` justamente por eso. La solución es borrar el entorno y volver a crearlo:

```
conda deactivate
conda env remove -n nwcst
conda env create -f environment.yml
```

**La computadora es institucional y no deja instalar.**
Es el problema que más demora y el único que no se arregla en la clínica. Escriba hoy al
área de sistemas pidiendo permiso para instalar Anaconda y Git.

**Todo lo demás.** Llévelo a la clínica con la captura de pantalla de
`verificar_entorno.py`. Con esa imagen el diagnóstico toma un minuto; sin ella, media hora.

---

## Resumen

```
conda --version                        # paso 1
git --version                          # paso 2
git clone https://github.com/guerreroda/nwcst_bol.git
cd nwcst_bol/code                      # paso 3
conda env create -f environment.yml    # paso 4
conda activate nwcst
python verificar_entorno.py            # paso 5
```
