import json
from django.utils.timezone import now, timedelta
import plotly.graph_objects as go
from plotly.offline import plot
from django.db.models import Count
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import openpyxl
from .models import AsignacionChofer, Camion, HistorialViaje
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UsuarioForm, CamionForm
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse


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
        return render(request, 'mapa.html')
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
            form.save()
            # Responde con JSON si es una solicitud AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})  # No redirige, responde con JSON
            return redirect('usuarios_list')  # Redirige solo si no es AJAX
        else:
            # Manejo de errores del formulario
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
            form.save()
            # Responder con JSON si es una solicitud AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Usuario actualizado correctamente'})
            # Redirigir si no es una solicitud AJAX
            return redirect('usuarios_list')
        else:
            # Responder con errores si es una solicitud AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = UsuarioForm(instance=usuario)
    # Pasa el objeto usuario al contexto
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

        # Crear un registro en HistorialViaje
        historial = HistorialViaje.objects.create(
            camion=asignacion.camion,
            chofer=request.user,
            fecha_inicio=timezone.now(),
            estado="En curso"
        )
        
        if historial:
            historial.fecha_fin = timezone.now()
            # Aquí se actualizan las coordenadas finales
            historial.latitud_inicial = asignacion.camion.latitud
            historial.longitud_inicial = asignacion.camion.longitud
            historial.save()

        
        # Actualizar la asignación para indicar que el viaje está activo
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

        # Actualizar el registro de HistorialViaje
        historial = HistorialViaje.objects.filter(
            camion=asignacion.camion, 
            chofer=request.user, 
            estado="En curso"
        ).order_by('-fecha_inicio').first()

        if historial:
            historial.fecha_fin = timezone.now()
            historial.estado = "Finalizado"
            # Aquí se actualizan las coordenadas finales
            historial.latitud_final = asignacion.camion.latitud
            historial.longitud_final = asignacion.camion.longitud
            historial.save()

        # Liberar el camión
        asignacion.en_viaje = False
        asignacion.fecha_fin = timezone.now()
        asignacion.save()

        asignacion.camion.choferes_asignados.remove(request.user)
        asignacion.camion.save()

        return JsonResponse({'status': 'Viaje finalizado', 'fecha_fin': historial.fecha_fin})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
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

    return render(request, 'historial_viajes.html', {'historial': historial})

@login_required
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


def estadistica(request):
    # Contar los viajes por chofer
    viajes_por_chofer = HistorialViaje.objects.values('chofer__username').annotate(cantidad_viajes=Count('id')).order_by('-cantidad_viajes')

    # Calcular los camiones conectados
    camiones = Camion.objects.all()
    choferes_online = sum(1 for camion in camiones if camion.esta_conectado())  # Contar los camiones conectados

    # Preparar los datos para el gráfico de barras
    nombres_choferes = [item['chofer__username'] for item in viajes_por_chofer]
    cantidad_viajes = [item['cantidad_viajes'] for item in viajes_por_chofer]

    # Crear el gráfico de barras con Plotly
    fig = go.Figure(data=[go.Bar(
        x=nombres_choferes,
        y=cantidad_viajes,
        text=cantidad_viajes,
        textposition='auto',
        marker=dict(color='royalblue')  # Color de las barras
    )])

    # Personalización del gráfico (tamaño, colores, fuentes)
    fig.update_layout(
        title="Viajes por Conductor",
        legend_title="Conductor",
        margin=dict(l=20, r=0, t=50, b=0),
        width=350,
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Convertir el gráfico de barras a HTML
    graph_html = plot(fig, output_type='div')

    # Crear el mapa con Plotly centrado en Santiago de Chile
    map_fig = go.Figure(go.Scattermapbox(
        mode='markers',
        lat=[-33.4489],  # Latitud de Santiago
        lon=[-70.6693],  # Longitud de Santiago
        text=["Santiago de Chile"],  # Texto que se muestra al pasar el mouse sobre el marcador
        marker=dict(size=12, color='blue', opacity=0.7),
    ))

    # Configuración del layout del mapa
    map_fig.update_layout(
        title="Mapa de Santiago de Chile",
        mapbox=dict(
            style="open-street-map",  # Estilo del mapa
            center=dict(lat=-33.4489, lon=-70.6693),  # Coordenadas de Santiago
            zoom=12,  # Zoom adecuado para la ciudad
            accesstoken="tu-token-de-mapbox",  # Asegúrate de usar tu token si usas Mapbox
            pitch=0,  # Deshabilitar inclinación del mapa
            bearing=0,  # Deshabilitar rotación del mapa
        ),
        height=600,  # Establecer la altura del mapa
        width=600,   # Establecer el ancho del mapa
        margin=dict(l=0, r=0, t=0, b=0),  # Eliminar márgenes
    )

    # Convertir el mapa a HTML
    map_html = plot(map_fig, output_type='div')

    # Contexto para la plantilla
    viajes_totales = HistorialViaje.objects.all()
        # Calcular viajes en curso
    viajes_en_curso = viajes_totales.filter(estado="En curso").count()

    # Calcular viajes completados
    viajes_completados = viajes_totales.filter(estado="Finalizado").count()

    # Calcular conductores online (camiones conectados)
    camiones_conectados = Camion.objects.filter(
        ultima_actualizacion__gte=now() - timedelta(minutes=5)
    ).count()



    context = {
        'viajes_totales': viajes_totales.count(),
        'viajes_en_curso': viajes_en_curso,
        'viajes_completados': viajes_completados,
        'graph_html': graph_html,
        'viajes_por_chofer': viajes_por_chofer,
        'choferes_online': choferes_online,
        'map_html': map_html  # Agregar el mapa al contexto
    }

    return render(request, 'estadistica.html', context)

