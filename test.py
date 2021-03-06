
import os 
import sys
import textwrap

EMAIL_TO = 'gabri005@gmail.com'
subject = 'ZABBIX LAB - Problem: {TRIGGER_NAME}'
BODY_EMAIL = '''
State of service "BrokerInfrastructure" (Background Tasks Infrastructure Service)@EVENT.ID@28310@00C800@3600@
<html>
<head>
<style type="text/css"></style>
</head>
<body>
<table class='alert' style="border:3px solid #666363;border-collapse:collapse;font-family:Verdana;font-size:10pt;">
<tr>
<th colspan="2" style="border-bottom:3px solid #666363;text-align:left;padding:5px;background-color:#eae8e8"><img src="https://www.morphus.com.br/static/website/img/logo.png" width="200" height="60"><center>SOC Morphus - Alertas Morphus SIEM.</center></th>
</tr>
<tr>
<td>Alerta: </td>
<td>Detectamos {TRIGGER_NAME}</td>
</tr>
<tr class='alt'>
<td style="background-color:#eae8e8;text-align:justify;padding:3px" >Host Impactado:</td>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">{HOST_NAME}</td>
</tr>
<tr>
<td>Tipo:</td>
<td>{TRIGGER_STATUS}</td>
</tr>
<tr class='alt'>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">Severidade:</td>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">{TRIGGER_SEVERITY}</td>
</tr>
<tr>
<td>Último valor coletado:</td>
<td>{ITEM_NAME1} ({HOST_NAME1}:{ITEM_KEY1}): {ITEM_VALUE1}</td>
</tr>
<tr>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">Recomendação:</td>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">Sugerimos a verificação do serviço e/ou dispositivo impactado a fim de evitar indisponibilidades no ambiente.</td>
</tr>
<tr>
<td>Data/Hora:</td>
<td>{DATE} às {TIME} - {TIMEZONE_FORTALEZA}</td>
</tr>
<tr>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">ID do Evento:</td>
<td style="background-color:#eae8e8;text-align:justify;padding:3px">{EVENT_ID}</td>
</tr>
<tr>
<td>Gráfico:</td>
<td><img src="cid:image1"</td>
</tr>
<tr>
<td>Histórico:</td>
<td>{HISTORY}</td>
</tr>
<tr>
<td style="background-color:#eae8e8;text-align:justify;padding:3px"><b>Observação:</b></td>
<td style="background-color:#eae8e8;text-align:justify;padding:3px"><b>Para apoio na tratativa desse evento, por favor
abra um chamado em nossa central de serviços <A href="https://servicedesk.morphus.com.br/" target="_blank">clicando aqui.<br /></A> Caso tenha dúvidas
sobre essa notificação, por favor, responda este e-mail.</b></td>
</tr>
</table>
</body>
</html>
'''
body = ''.join(textwrap.wrap(BODY_EMAIL))
os.system("python email_alert.py gabri005@gmail.com assunto '{0}'".format(body))