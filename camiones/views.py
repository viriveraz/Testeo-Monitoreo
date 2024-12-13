import json
from django.db.models.functions import TruncMonth
import plotly.graph_objects as go
from plotly.offline import plot
from datetime import datetime, timedelta
from django.db.models import Count
from datetime import datetime
from django.db.models import Count, Avg
from django.utils.timezone import now, timedelta
import plotly.graph_objects as go
from plotly.offline import plot
from django.db.models import Count
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import openpyxl
from .models import AsignacionChofer, Camion, HistorialViaje, Chofer, MensajePredefinido
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import UsuarioForm, CamionForm
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse
from camiones.utils import enviar_mensaje_whatsapp

# Obtener ubicación del camión
def obtener_ubicacion(request, camion_id):
    try:
        camion = Camion.objects.get(id=camion_id)
        return JsonResponse({
            'latitud': camion.latitud,
            'longitud': camion.longitud
        })
    except Camion.DoesNotExist:
        return JsonResponse({'error': 'Camión no encontrado'}, status=404)

@login_required
def mostrar_mapa(request):
    if request.user.is_staff:
        mensajes_predefinidos = MensajePredefinido.objects.all()
        choferes = Chofer.objects.all()  # Obtener todos los choferes
        print(choferes)  # Para verificar si hay choferes en la consola
        return render(request, 'mapa.html', {'mensajes_predefinidos': mensajes_predefinidos, 'choferes': choferes})
    else:
        return render(request, 'mapa_chofer.html')

@login_required
@csrf_protect
def actualizar_ubicacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitud = data.get('latitud')
            longitud = data.get('longitud')

            if latitud is None or longitud is None:
                return JsonResponse({'error': 'Faltan coordenadas en la solicitud'}, status=400)

            # Obtener la asignación activa para el chofer actual
            asignacion = AsignacionChofer.objects.filter(
                chofer=request.user,
                fecha_fin__isnull=True  # Asignación activa
            ).first()

            if not asignacion:
                return JsonResponse({'error': 'No hay camión asignado al conductor'}, status=400)

            dispositivo = asignacion.camion
            dispositivo.latitud = latitud
            dispositivo.longitud = longitud
            dispositivo.ultima_actualizacion = timezone.now()
            dispositivo.save()

            print(f"Actualizando ubicación para el camión: {dispositivo.nombre}")
            return JsonResponse({'status': 'Ubicación actualizada exitosamente'})

        except Exception as e:
            print(f"Error en actualizar_ubicacion: {e}")  # Línea de depuración
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)




@login_required
def dispositivos_admin_view(request):
    dispositivos_conectados = Camion.objects.filter(
        ultima_actualizacion__gte=timezone.now() - timezone.timedelta(minutes=5)
    )
    return render(request, 'dispositivos_admin.html', {'dispositivos': dispositivos_conectados})

@login_required
def dispositivos_chofer_view(request):
    asignacion = AsignacionChofer.objects.filter(chofer=request.user, fecha_fin__isnull=True).first()
    
    if asignacion:
        dispositivo = asignacion.camion
        return render(request, 'dispositivos_chofer.html', {'dispositivo': dispositivo})
    else:
        # Redirige a una página que indique que no hay camión asignado
        return render(request, 'no_camion_disponible.html', {
            'mensaje': 'No tienes un camión asignado en este momento.'
        })

@login_required
def obtener_ubicaciones(request):
    dispositivos_conectados = Camion.objects.filter(
        ultima_actualizacion__gte=timezone.now() - timezone.timedelta(minutes=5)
    )
    data = [{'latitud': dispositivo.latitud, 'longitud': dispositivo.longitud} for dispositivo in dispositivos_conectados]
    return JsonResponse({'dispositivos': data})

# Vistas para usuarios
def usuarios_list(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})

def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            # Crea el usuario pero no guarda la contraseña como texto plano
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])  # Encripta la contraseña
            usuario.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})  # Responde con JSON si es AJAX
            return redirect('usuarios_list')  # Redirige si no es AJAX
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = UsuarioForm()
    return render(request, 'usuario_crear.html', {'form': form})

def usuario_update(request, id):
    usuario = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            # Solo actualiza la contraseña si fue proporcionada
            if form.cleaned_data.get('password'):
                usuario.set_password(form.cleaned_data['password'])  # Encripta la contraseña
            usuario.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Usuario actualizado correctamente'})
            return redirect('usuarios_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuario_edit.html', {'form': form, 'usuario': usuario})

def usuario_delete(request, id):
    usuario = get_object_or_404(User, id=id)
    if request.method == 'POST':
        usuario.delete()
        # Responder con JSON si es una solicitud AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Usuario eliminado correctamente'})
        # Redirigir si no es una solicitud AJAX
        return redirect('usuarios_list')
    return render(request, 'usuario_confirm_delete.html', {'usuario': usuario})

# Vistas para camiones
def camiones_list(request):
    camiones = Camion.objects.all()
    return render(request, 'camiones_list.html', {'camiones': camiones})



def camion_create(request):
    if request.method == 'POST':
        form = CamionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Camión añadido exitosamente.")
            return redirect('camiones_list')
        else:
            messages.error(request, "Error al añadir el camión.")
    else:
        form = CamionForm()
    return render(request, 'camion_form.html', {'form': form})

def camion_update(request, id):
    camion = get_object_or_404(Camion, id=id)
    if request.method == 'POST':
        form = CamionForm(request.POST, instance=camion)
        if form.is_valid():
            form.save()
            return redirect('camiones_list')
    else:
        form = CamionForm(instance=camion)
    return render(request, 'camion_edit.html', {'form': form})

def camion_delete(request, id):
    camion = get_object_or_404(Camion, id=id)
    if request.method == 'POST':
        camion.delete()
        messages.success(request, "Camión eliminado exitosamente.")
        return redirect('camiones_list')
    return render(request, 'camion_confirm_delete.html', {'camion': camion})

@login_required
def asignar_camion_automatico(request):
    chofer = request.user
    # Buscar el primer camión disponible (sin chofer asignado actualmente)
    camion_disponible = Camion.objects.filter(choferes_asignados__isnull=True).first()
    
    if camion_disponible:
        # Asignar el camión al chofer
        AsignacionChofer.objects.create(chofer=chofer, camion=camion_disponible, fecha_inicio=timezone.now())
        return redirect('vista_conductor')  # Redirige a la vista de monitoreo del chofer
    else:
        # Si no hay camiones disponibles, renderiza la página no_camion_disponible
        return render(request, 'no_camion_disponible.html', {
            'mensaje': 'No hay camiones disponibles para asignar en este momento.'
        })


@login_required
def iniciar_viaje(request):
    try:
        asignacion = AsignacionChofer.objects.filter(
            chofer=request.user, 
            fecha_fin__isnull=True, 
            en_viaje=False
        ).order_by('-fecha_inicio').first()

        if not asignacion:
            return JsonResponse({'error': 'No hay camión asignado o el viaje ya está en curso'}, status=400)
        
        camion = asignacion.camion

        # Extraer latitud y longitud actuales del camión
        latitud_inicial = camion.latitud
        longitud_inicial = camion.longitud

        if latitud_inicial is None or longitud_inicial is None:
            return JsonResponse({'error': 'No se pueden obtener las coordenadas del camión asignado.'}, status=400)


        # Crear un registro en HistorialViaje
        historial = HistorialViaje.objects.create(
            camion=asignacion.camion,
            chofer=request.user,
            fecha_inicio=now(),
            latitud_inicial=latitud_inicial,
            longitud_inicial=longitud_inicial,
            estado="En curso"
        )

        # Enviar mensaje de WhatsApp con las coordenadas iniciales
        mensaje = f"Inicio de viaje en el camión {camion.nombre}.\nCoordenadas iniciales:\nLatitud: {latitud_inicial}\nLongitud: {longitud_inicial}"
        chofer = Chofer.objects.get(usuario=request.user)  # Obtener el modelo Chofer relacionado
        enviar_mensaje_whatsapp(chofer.telefono, chofer.api_key, mensaje)

        # Actualizar asignación
        asignacion.en_viaje = True
        asignacion.save()

        return JsonResponse({'status': 'Viaje iniciado', 'fecha_inicio': historial.fecha_inicio})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)  

@login_required
def finalizar_viaje(request):
    try:
        asignacion = AsignacionChofer.objects.filter(
            chofer=request.user, 
            fecha_fin__isnull=True, 
            en_viaje=True
        ).order_by('-fecha_inicio').first()

        if not asignacion:
            return JsonResponse({'error': 'No hay un viaje activo para finalizar'}, status=400)

        camion = asignacion.camion

        # Extraer latitud y longitud actuales del camión
        latitud_final = camion.latitud
        longitud_final = camion.longitud

        if latitud_final is None or longitud_final is None:
            return JsonResponse({'error': 'No se pueden obtener las coordenadas del camión asignado.'}, status=400)


        # Actualizar el registro de HistorialViaje
        historial = HistorialViaje.objects.filter(
            camion=asignacion.camion, 
            chofer=request.user, 
            estado="En curso"
        ).order_by('-fecha_inicio').first()

        if historial:
            historial.fecha_fin = now()
            historial.latitud_final = latitud_final
            historial.longitud_final = longitud_final
            historial.estado = "Finalizado"
            historial.duracion_total = historial.fecha_fin - historial.fecha_inicio
            historial.save()

        # Enviar mensaje de WhatsApp con las coordenadas finales
        mensaje = f"Finalización de viaje en el camión {camion.nombre}.\nCoordenadas finales:\nLatitud: {latitud_final}\nLongitud: {longitud_final}\nDuración del viaje: {historial.duracion_formateada}"
        chofer = Chofer.objects.get(usuario=request.user)
        enviar_mensaje_whatsapp(chofer.telefono, chofer.api_key, mensaje)

        # Liberar el camión
        asignacion.en_viaje = False
        asignacion.fecha_fin = now()
        asignacion.save()

        return JsonResponse({'status': 'Viaje finalizado', 'duracion_total': str(historial.duracion_total)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)




def historial_viajes(request):
    historial = HistorialViaje.objects.all()

    if not request.user.is_staff:  # Mostrar solo viajes del chofer
        historial = historial.filter(chofer=request.user)

    # Filtros opcionales
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    camion_id = request.GET.get('camion_id')

    if fecha_inicio:
        historial = historial.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        historial = historial.filter(fecha_fin__lte=fecha_fin)
    if camion_id:
        historial = historial.filter(camion_id=camion_id)

    # Generar mapa con Plotly
    puntos = []
    textos = []

    for viaje in historial:
        if viaje.latitud_inicial and viaje.longitud_inicial:
            puntos.append((viaje.latitud_inicial, viaje.longitud_inicial))
            textos.append(f"Inicio: {viaje.camion.nombre}, {viaje.chofer.first_name} {viaje.chofer.last_name}")

        if viaje.latitud_final and viaje.longitud_final:
            puntos.append((viaje.latitud_final, viaje.longitud_final))
            textos.append(f"Fin: {viaje.camion.nombre}, {viaje.chofer.first_name} {viaje.chofer.last_name}")

    if puntos:
        latitudes, longitudes = zip(*puntos)
        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            lat=latitudes,
            lon=longitudes,
            text=textos,
            marker=dict(size=10, color='blue'),
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=5,
                center=dict(lat=sum(latitudes) / len(latitudes), lon=sum(longitudes) / len(longitudes)),
            ),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        map_html = plot(fig, output_type="div")
    else:
        map_html = "<p>No hay datos para mostrar en el mapa.</p>"

    return render(request, 'historial_viajes.html', {
        'historial': historial,
        'map_html': map_html,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })


    
def historial_viajes_chofer(request):
    historial = HistorialViaje.objects.all()

    if not request.user.is_staff:  # Mostrar solo viajes del chofer
        historial = historial.filter(chofer=request.user)

    # Filtros opcionales
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    camion_id = request.GET.get('camion_id')

    if fecha_inicio:
        historial = historial.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        historial = historial.filter(fecha_fin__lte=fecha_fin)
    if camion_id:
        historial = historial.filter(camion_id=camion_id)

    return render(request, 'historial_viajes_chofer.html', {'historial': historial})

@login_required
def eliminar_viaje(request, viaje_id):
    viaje = get_object_or_404(HistorialViaje, id=viaje_id, chofer=request.user)
    viaje.delete()
    return redirect('historial_viajes')  # Redirige a la lista de viajes

@login_required
def exportar_historial_excel(request):
    viajes = HistorialViaje.objects.filter(chofer=request.user).order_by('-fecha_inicio')

    # Crear un libro de Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Historial de Viajes"

    # Agregar encabezados
    headers = ["Camión", "Chofer", "Fecha Inicio", "Fecha Fin", "Estado"]
    sheet.append(headers)

    # Agregar datos
    for viaje in viajes:
        sheet.append([
            viaje.camion.nombre,
            viaje.chofer.username,
            viaje.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
            viaje.fecha_fin.strftime('%Y-%m-%d %H:%M:%S') if viaje.fecha_fin else "En curso",
            viaje.estado
        ])

    # Preparar la respuesta HTTP
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename="historial_viajes.xlsx"'
    workbook.save(response)
    return response


def esta_conectado(self):
    return timezone.now() - self.ultima_actualizacion <= timezone.timedelta(minutes=5)



def generar_mapa_plotly(historial_viajes):
    puntos = []
    textos = []

    for viaje in historial_viajes:
        if viaje.latitud_inicial and viaje.longitud_inicial:
            puntos.append((viaje.latitud_inicial, viaje.longitud_inicial))
            textos.append(f"Inicio: {viaje.chofer.first_name} {viaje.chofer.last_name} ({viaje.camion.nombre})")

        if viaje.latitud_final and viaje.longitud_final:
            puntos.append((viaje.latitud_final, viaje.longitud_final))
            textos.append(f"Fin: {viaje.chofer.first_name} {viaje.chofer.last_name} ({viaje.camion.nombre})")

    if puntos:
        latitudes, longitudes = zip(*puntos)
        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            lat=latitudes,
            lon=longitudes,
            text=textos,
            marker=dict(size=10, color='blue'),
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=3,
                center=dict(lat=sum(latitudes) / len(latitudes), lon=sum(longitudes) / len(longitudes)),
            ),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return plot(fig, output_type="div")

    return "<p>No hay datos para mostrar en el mapa.</p>"



def estadistica(request):
    # Filtrar por rango de fechas si están presentes
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    viajes_totales = HistorialViaje.objects.all()

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            viajes_totales = viajes_totales.filter(fecha_inicio__date__gte=fecha_inicio, fecha_fin__date__lte=fecha_fin)
        except ValueError:
            pass
    else:
        # Si no se proporcionaron fechas, obtener el primer y último día del mes actual
        today = datetime.today()
        fecha_inicio = today.replace(day=1)  # Primer día del mes actual
        next_month = today.replace(day=28) + timedelta(days=4)  # Esto siempre nos da un día en el siguiente mes
        fecha_fin = next_month - timedelta(days=next_month.day)  # Último día del mes actual

        viajes_totales = viajes_totales.filter(fecha_inicio__date__gte=fecha_inicio, fecha_fin__date__lte=fecha_fin)

    # Variable para verificar si hay viajes
    sin_viajes = not viajes_totales.exists()

    # Datos para los gráficos y mapa si hay viajes
    viajes_por_chofer = []
    viajes_por_mes = []
    graph_html_mes = ""
    graph_html_conductor = ""
    map_html = ""

    if not sin_viajes:
        # Gráfico de cantidad de viajes por mes
        viajes_por_mes = viajes_totales.annotate(mes=TruncMonth('fecha_inicio')) \
            .values('mes') \
            .annotate(cantidad_viajes=Count('id')) \
            .order_by('mes')

        # Crear una lista con los meses y las cantidades de viajes
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        viajes_por_mes_dict = {mes: 0 for mes in meses}
        for item in viajes_por_mes:
            mes = item['mes'].month - 1  # Ajustar para índice 0 basado
            viajes_por_mes_dict[meses[mes]] = item['cantidad_viajes']

        # Crear el gráfico de viajes por mes (puntos y línea)
        fig_mes = go.Figure(data=[go.Scatter(
            x=meses,
            y=[viajes_por_mes_dict[mes] for mes in meses],
            mode='lines+markers',
            marker=dict(color='#4CAF50', size=8),
            line=dict(color='#4CAF50', width=2),
            text=[viajes_por_mes_dict[mes] for mes in meses],
            textposition='top center'
        )])

        fig_mes.update_layout(
            title="Cantidad de Viajes por Mes (Últimos 12 meses)",
            width=1750,
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True),
            showlegend=False
        )
        graph_html_mes = plot(fig_mes, output_type='div')

        # Gráfico de viajes por conductor
        viajes_por_chofer = viajes_totales.values(
            'chofer__first_name', 'chofer__last_name'
        ).annotate(
            cantidad_viajes=Count('id'),
            tiempo_promedio=Avg('duracion_total')
        ).order_by('-cantidad_viajes')

        for item in viajes_por_chofer:
            item['nombre_completo'] = f"{item['chofer__first_name']} {item['chofer__last_name']}"
            if item['tiempo_promedio']:
                item['tiempo_promedio'] = item['tiempo_promedio'].total_seconds() / 60  # Convertir a minutos
            else:
                item['tiempo_promedio'] = 0

        # Crear el gráfico de viajes por conductor
        fig_conductor = go.Figure(data=[go.Bar(
            x=[item['nombre_completo'] for item in viajes_por_chofer],
            y=[item['cantidad_viajes'] for item in viajes_por_chofer],
            text=[item['cantidad_viajes'] for item in viajes_por_chofer],
            textposition='auto',
            marker=dict(color='#4CAF50')
        )])
        fig_conductor.update_layout(
            title="Viajes por Conductor",
            width=350,
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        graph_html_conductor = plot(fig_conductor, output_type='div')

        # Obtener las coordenadas de los viajes filtrados para el mapa
        latitudes = []
        longitudes = []
        textos = []

        for viaje in viajes_totales:
            if viaje.latitud_final and viaje.longitud_final:
                latitudes.append(viaje.latitud_final)
                longitudes.append(viaje.longitud_final)
                textos.append(f"Viaje ID: {viaje.id}, {viaje.chofer.first_name} {viaje.chofer.last_name}")

        if latitudes:
            map_fig = go.Figure(go.Scattermapbox(
                mode='markers',
                lat=latitudes,
                lon=longitudes,
                text=textos,
                marker=dict(size=12, color='#4CAF50'),
            ))
            map_fig.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=sum(latitudes)/len(latitudes), lon=sum(longitudes)/len(longitudes)),
                    zoom=10,
                ),
                height=300,
                width=800,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
            )
            map_html = plot(map_fig, output_type='div')

        choferes_en_linea = viajes_totales.filter(estado="En curso").values('chofer__username').distinct().count()

    context = {
        'viajes_totales': viajes_totales.count(),
        'viajes_en_curso': viajes_totales.filter(estado="En curso").count(),
        'viajes_completados': viajes_totales.filter(estado="Finalizado").count(),
        'graph_html_mes': graph_html_mes,
        'graph_html_conductor': graph_html_conductor,
        'viajes_por_chofer': viajes_por_chofer,
        'map_html': map_html,
        'sin_viajes': sin_viajes,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'choferes_en_linea': choferes_en_linea,
    }
    return render(request, 'estadistica.html', context)



@login_required
@user_passes_test(lambda u: u.is_staff)
def enviar_mensaje_predefinido(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mensaje_id = data.get("mensaje_id")
            mensaje_personalizado = data.get("mensaje_personalizado", "").strip()
            chofer_ids = data.get("chofer_ids", [])

            # Validar mensaje
            if not mensaje_id and not mensaje_personalizado:
                return JsonResponse({"status": "error", "mensaje": "Debes proporcionar un mensaje válido."})

            # Usar mensaje personalizado si no hay un mensaje predefinido seleccionado
            mensaje_cuerpo = ""
            if mensaje_id:
                try:
                    mensaje = MensajePredefinido.objects.get(id=mensaje_id)
                    mensaje_cuerpo = mensaje.cuerpo
                except MensajePredefinido.DoesNotExist:
                    return JsonResponse({"status": "error", "mensaje": "El mensaje predefinido seleccionado no existe."})
            elif mensaje_personalizado:
                mensaje_cuerpo = mensaje_personalizado

            # Filtrar choferes seleccionados
            choferes = Chofer.objects.filter(id__in=chofer_ids, telefono__isnull=False, api_key__isnull=False)

            resultados = []
            for chofer in choferes:
                cuerpo_personalizado = mensaje_cuerpo.replace("[NOMBRE_CHOFER]", chofer.usuario.username)
                exito = enviar_mensaje_whatsapp(chofer.telefono, chofer.api_key, cuerpo_personalizado)
                resultados.append({
                    "chofer": chofer.usuario.username,
                    "numero": chofer.telefono,
                    "resultado": "Éxito" if exito else "Fallo"
                })

            return JsonResponse({"status": "completado", "detalles": resultados})

        except Exception as e:
            return JsonResponse({"status": "error", "mensaje": str(e)})

    return JsonResponse({"status": "error", "mensaje": "Método no permitido."}, status=405)