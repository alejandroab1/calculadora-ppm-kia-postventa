// -----------------------------------------------------------------------
// DATOS DE ANEXOS EXTRAÍDOS DESDE EXCEL
// Funciones para buscar y renderizar tablas de mantenimiento dinámicas
// ------- -----------------------------------------------------------------------

// Función para encontrar la tabla de anexos según modelo y plan
function findAnnexTable(modelo, plan) {
  var modeloCompleto = (modelo || '').trim().toUpperCase();
  var firstWord = modeloCompleto.split(' ')[0]; // Extraer primera palabra
  var isUL = (plan || '').trim().toLowerCase().indexOf('unlimited') >= 0;
  
  console.log('🔍 Buscando anexo:');
  console.log('   Modelo completo:', modeloCompleto);
  console.log('   Primera palabra:', firstWord);
  console.log('   Plan:', plan, '(Unlimited:', isUL, ')');
  
  // Datos desde Excel - estructura de celdas B2
  var fullserviceAnnexes = [
    { nombres: 'PICANTO, SOLUTO, SONET K3, TASMAN', palabras: ['PICANTO', 'SOLUTO', 'SONET', 'TASMAN', 'K3'] },
    { nombres: 'SELTOS, SPORTAGE, SORENTO, CARNIVAL, CARENS', palabras: ['SELTOS', 'SPORTAGE', 'SORENTO', 'CARNIVAL', 'CARENS'] },
    { nombres: 'EV5', palabras: ['EV5'] },
    { nombres: 'EV9', palabras: ['EV9'] },
    { nombres: 'NIRO', palabras: ['NIRO'] },
    { nombres: 'TOWNER', palabras: ['TOWNER'] }
  ];
  
  var unlimitedAnnexes = [
    { nombres: 'PICANTO, SOLUTO, RIO, CERATO, SONET K3, TASMAN', palabras: ['PICANTO', 'SOLUTO', 'RIO', 'CERATO', 'SONET', 'TASMAN', 'K3'] },
    { nombres: 'SELTOS, SPORTAGE, SORENTO, CARNIVAL, CARENS', palabras: ['SELTOS', 'SPORTAGE', 'SORENTO', 'CARNIVAL', 'CARENS'] },
    { nombres: 'NIRO', palabras: ['NIRO'] },
    { nombres: 'TOWNER', palabras: ['TOWNER'] }
  ];
  
  var annexList = isUL ? unlimitedAnnexes : fullserviceAnnexes;
  
  // Buscar la primera palabra en la lista de anexos
  for (var i = 0; i < annexList.length; i++) {
    var anexo = annexList[i];
    console.log('   Buscando en anexo', i + 1, 'con modelos:', anexo.nombres);
    for (var j = 0; j < anexo.palabras.length; j++) {
      if (firstWord === anexo.palabras[j]) {
        console.log('   ✅ ¡Encontrado! Coincide con:', anexo.palabras[j]);
        return {
          modelo: anexo.nombres,
          tipo: isUL ? 'unlimited' : 'fullservice',
          primeraPalabra: firstWord
        };
      }
    }
  }
  
  console.log('   ❌ No encontrado');
  return null;
}

console.log('Funciones de anexos dinámicos cargadas correctamente');

// -----------------------------------------------------------------------
// HELPERS PARA CONTRATO 2 SERVICIOS
// -----------------------------------------------------------------------
var _kmMesesTbl = {
  '5K':  {5000:6,10000:12,15000:18,20000:24,25000:30,30000:36,35000:42,40000:48,45000:54,50000:60,55000:66,60000:72,65000:78,70000:84,75000:90,80000:96,85000:102,90000:108,95000:114,100000:120},
  '10K': {5000:6,10000:12,20000:24,30000:36,40000:48,50000:60,60000:72,70000:84,80000:96,90000:108,100000:120},
  '15K': {15000:12,30000:24,45000:36,60000:48,75000:60,90000:72,105000:84,120000:96}
};
function kmToLabel(kmStr){var n=parseInt(kmStr)*1000;return n.toLocaleString('es-PE')+' KM';}
function kmToMeses(kmStr,freq){var n=parseInt(kmStr)*1000;var tbl=_kmMesesTbl[freq]||_kmMesesTbl['10K'];return tbl[n]||null;}
function mesesLabel(m){if(!m)return null;return m>=12?(m/12)+'  año'+(m/12>1?'s':''):m+' mes'+(m>1?'es':'');}
function getDSServices(f){
  try{
    var plan=f.Plan||'';var modelo=f.Modelo||'';var config=f.Configuracion||'';
    var pm=plan.match(/(\d+K)\s*\+\s*(\d+K)/i);if(!pm)return null;
    var km1=pm[1].toUpperCase(),km2=pm[2].toUpperCase(),par=km1+'-'+km2;
    var fm=config.match(/\b(5K|10K|15K)\b/i);var freq=fm?fm[1].toUpperCase():'';
    var keys=Object.keys(DS.servicios||{});
    for(var i=0;i<keys.length;i++){
      var k=keys[i];var kp=k.split('|');
      if(kp[0]===modelo&&kp[3]===freq&&DS.servicios[k]&&DS.servicios[k][par])
        return{ops1:DS.servicios[k][par][0]||[],ops2:DS.servicios[k][par][1]||[]};
    }
    return null;
  }catch(e){return null;}
}
function buildAnexoDS(f,km1,km2){
  var svc=getDSServices(f);
  if(!svc)return '<p style="font-size:9.5pt;color:#666;margin-top:8px">Ver detalle de servicios en la cotización adjunta.</p>';
  function renderOps(opsIdx){
    if(!opsIdx.length)return '<p style="font-size:7.5pt;color:#888">Sin operaciones</p>';
    var moOps=[],gasOps=[];
    opsIdx.forEach(function(i){var raw=DS.ops[parseInt(i)]||'';var isGas=raw.indexOf('[GAS]')===0;var clean=raw.replace(/^\[(?:MO|GAS)\]\s*/,'');(isGas?gasOps:moOps).push(clean);});
    var h='';
    if(moOps.length)h+='<ul style="margin:1px 0 3px 11px;font-size:7.5pt">'+moOps.map(function(o){return'<li>'+o+'</li>';}).join('')+'</ul>';
    if(gasOps.length)h+='<strong style="font-size:7.5pt">Insumos:</strong><ul style="margin:1px 0 3px 11px;font-size:7.5pt">'+gasOps.map(function(o){return'<li>'+o+'</li>';}).join('')+'</ul>';
    return h;
  }
  return'<table style="width:100%;box-sizing:border-box;border-collapse:collapse;font-size:7.5pt;border:1px solid #000;margin-top:4px"><tr style="background:#000;color:#fff"><th style="padding:3px 6px;border:1px solid #000;width:50%;text-align:left">SERVICIO 1 — '+kmToLabel(km1)+'</th><th style="padding:3px 6px;border:1px solid #000;width:50%;text-align:left">SERVICIO 2 — '+kmToLabel(km2)+'</th></tr><tr><td style="padding:4px 6px;border:1px solid #ccc;vertical-align:top">'+renderOps(svc.ops1)+'</td><td style="padding:4px 6px;border:1px solid #ccc;vertical-align:top">'+renderOps(svc.ops2)+'</td></tr></table>';
}

function getRevisionesContratoHTML(modeloAuto,freq,s1,s2,s3,s4){
  var m=(modeloAuto||'').toUpperCase();
  var isEV=freq==='15K'&&/EV5|EV9|\bEV\b/.test(m);
  var isHEV=!isEV&&freq==='15K';
  function cH(t){return'<div style="font-size:7pt;font-weight:700;text-transform:uppercase;color:#05141F;padding-bottom:2px;margin-bottom:2px;border-bottom:1px solid #ccc;">'+t+'</div>';}
  function cS(t){return'<div style="font-size:7pt;font-weight:600;color:#333;margin-top:2px;margin-bottom:1px;">'+t+'</div>';}
  function cI(t){return'<li style="font-size:7pt;color:#1a1a1a;line-height:1.3;padding-left:5px;text-indent:-5px">&bull; '+t+'</li>';}
  function cU(items){return'<ul style="list-style:none;padding:0;margin:0;">'+items.filter(function(x){return x;}).join('')+'</ul>';}
  var col1a=cH('En el Vehículo')+cU([cI('Actualizar indicador de mantenimiento'),cI('Bocina'),cI('Eyectores limpiaparabrisas'),cI('Luces / alumbrado / señalización'),cI('Juego libre del timón'),cI('Operación A/C'),(!isEV?cI('Filtro de Habitáculo'):''),(!isHEV&&!isEV?cI('Recorrido del embrague'):''),cI('Cinturones de seguridad')]);
  var col1b=cH('Debajo del Vehículo')+cU([(isEV?cI('Fugas del engranaje de reducción'):cI('Fugas en carter y caja')),cI('Fugas en sistema de refrigeración'),cI('Fugas en amortiguadores'),cI('Fugas en circuito de frenos'),(!isEV?cI('Fugas en sistema de combustible'):''),cI('Elementos de dirección'),(!isEV?cI('Tubo de escape y sus soportes'):''),cI('Elementos de suspensión'),cI('Ejes y palieres')]);
  var col1c=cH('Alrededor del Vehículo')+cU([cI('Estado y presión de neumáticos'),cI('Faros y micas de luces'),cI('Plumillas de limpiaparabrisas'),(isHEV?cI('Tapa de llenado de combustible y manguera de vapor'):'')]);
  var col1d=cH('Bajo el Capó')+cU([(!isEV?cI('Nivel de aceite motor'):''),cI('Nivel de limpiaparabrisas'),cI('Nivel y condición de refrigerante'),cI('Nivel de líquido de frenos'),cI('Fugas en circuitos de frenos'),(!isEV?(isHEV?cI('Fajas de accesorios y/o faja HSG'):cI('Fajas de accesorios')):''),(!isEV?(isHEV?cI('Filtro de aire y revestimiento de goma'):cI('Filtro de aire')):''),cI('Estado y carga de batería'+(isHEV||isEV?' de 12V.':''))]);
  var col2=cH('(2) Revisión de Frenos')+cS('Verificar:')+cU([cI('Desgaste discos y pastillas'),cI('Desgaste tambores y zapatas'+(isHEV||isEV?' (Si equipa)':'')),cI('Fugas en calipers, bombines y mangueras')])+cS(isHEV||isEV?'Inspección:':'Regular:')+cU([cI(isHEV||isEV?'Freno de estacionamiento':'Freno de mano')]);
  var col3=isEV?(cH('(3) Rev. Líneas de Refrigeración')+cS('Verificar:')+cU([cI('Mangueras del sistema de refrigeración'),cI('Abrazaderas de las mangueras de refrigeración')])):(cH('(3) Rev. Admisión y Gases')+cS('Verificar:')+cU([cI('Mangueras de vacío de motor'),cI('Mangueras de ventilación de cárter (PCV)')])+cS('Limpiar:')+cU([cI('Cámara de aceleración')]));
  var col4=isEV?(cH('(4) Observaciones')+cS('Verificar:')+cU([cI('Tapa de carga eléctrica de alta tensión'),cI('Conector de carga de alta tensión'),cI('Cable y conector de interface de carga')])):(cH('(4) Rev. Tanque de Combustible')+cS('Verificar:')+cU([cI('Mangueras de vapor de combustible'),cI('Fugas y ajuste de abrazaderas'),cI('Tapa de tanque de combustible'+(isHEV?' y manguera de vapor':''))]));
  if(s1===undefined)s1=true;if(s2===undefined)s2=true;if(s3===undefined)s3=true;if(s4===undefined)s4=true;
  if(!s1&&!s2&&!s3&&!s4)return'';
  var sec1HTML=s1?('<div style="background:#f0f0f0;padding:3px 10px;font-size:7pt;font-weight:700;text-transform:uppercase;color:#333;border-bottom:1px solid #ccc;">(1) REVISIONES DE SERVICIO &mdash; Verificar y ajustar</div>'
    +'<table style="width:100%;border-collapse:collapse;border-bottom:1px solid #ccc;"><tr>'
    +'<td style="padding:4px 6px;vertical-align:top;border:1px solid #ddd;width:25%">'+col1a+'</td>'
    +'<td style="padding:4px 6px;vertical-align:top;border:1px solid #ddd;width:25%">'+col1b+'</td>'
    +'<td style="padding:4px 6px;vertical-align:top;border:1px solid #ddd;width:25%">'+col1c+'</td>'
    +'<td style="padding:4px 6px;vertical-align:top;border:1px solid #ddd;width:25%">'+col1d+'</td>'
    +'</tr></table>'):'';
  var s234cols=[];if(s2)s234cols.push(col2);if(s3)s234cols.push(col3);if(s4)s234cols.push(col4);
  var s234w=s234cols.length===3?'33.33':s234cols.length===2?'50':'100';
  var sec234HTML=s234cols.length?('<table style="width:100%;border-collapse:collapse;"><tr>'+s234cols.map(function(c){return'<td style="padding:4px 6px;vertical-align:top;border:1px solid #ddd;width:'+s234w+'%">'+c+'</td>';}).join('')+'</tr></table>'):''
;  return'<div style="margin-top:6px;width:100%;box-sizing:border-box;border:1px solid #ccc;font-family:Arial,sans-serif;">'
    +'<div style="background:#05141F;color:white;padding:4px 10px;font-size:8.5pt;font-weight:700;text-transform:uppercase;letter-spacing:1px;">REVISIONES INCLUIDAS EN EL PLAN</div>'
    +sec1HTML+sec234HTML+'</div>';
}

// -----------------------------------------------------------------------
// CONTRATO 2 SERVICIOS
// -----------------------------------------------------------------------
function buildContratoDS(f, vin, dni) {
  var modelo = f.Modelo || '—';
  var cliente = f.Cliente || '—';
  var planLabel = f.Plan || '—';
  var ppm = f.Precio_PPM ? '$' + parseFloat(f.Precio_PPM).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',') : '—';
  var reg = f.Precio_Regular ? '$' + parseFloat(f.Precio_Regular).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',') : '—';
  var cot = f.Num_Cotizacion ? '#' + f.Num_Cotizacion : '';
  var fecha = fmtFecha();
  var config = f.Configuracion || '';
  // Extraer km1, km2 del plan "2 Servicios 5K + 10K"
  var pm = planLabel.match(/(\d+K)\s*\+\s*(\d+K)/i);
  var km1 = pm ? pm[1].toUpperCase() : '';
  var km2 = pm ? pm[2].toUpperCase() : '';
  // Frecuencia desde Configuracion
  var fm = config.match(/\b(5K|10K|15K)\b/i);
  var freq = fm ? fm[1].toUpperCase() : '10K';
  // Meses para cada servicio
  var m1 = km1 ? kmToMeses(km1, freq) : null;
  var m2 = km2 ? kmToMeses(km2, freq) : null;
  var row1 = km1 ? (kmToLabel(km1) + (m1 ? ' o ' + mesesLabel(m1) + ' de antigüedad del vehículo, lo que ocurra primero.' : '')) : '—';
  var row2 = km2 ? (kmToLabel(km2) + (m2 ? ' o ' + mesesLabel(m2) + ' de antigüedad del vehículo, lo que ocurra primero.' : '')) : '—';
  // Vigencia según frecuencia
  var vigencia = freq === '5K' ? '6 (seis) meses' : '1 (un) año';
  // Primer KM para la descripción
  var km1num = km1 ? parseInt(km1)*1000 : null;
  var km1txt = km1num ? km1num.toLocaleString('es-PE') : '—';
  var _dsOps=getDSServices(f);var _dsOpsTxt=_dsOps?((_dsOps.ops1||[]).concat(_dsOps.ops2||[])).map(function(i){return DS.ops[parseInt(i)]||'';}).join(' '):'';var csHasS1=!_dsOpsTxt||_dsOpsTxt.indexOf('(1)')!==-1;var csHasS2=!_dsOpsTxt||_dsOpsTxt.indexOf('(2)')!==-1;var csHasS3=!_dsOpsTxt||_dsOpsTxt.indexOf('(3)')!==-1;var csHasS4=!_dsOpsTxt||_dsOpsTxt.indexOf('(4)')!==-1;

  return contratoStyles() + `
  <div class="ct">
    <h1>TÉRMINOS Y CONDICIONES DEL</h1>
    <h2>PROGRAMA DE MANTENIMIENTOS KIA 2 SERVICIOS</h2>

    <div class="section-title">1. DESCRIPCIÓN</div>
    <p>El Programa de Mantenimientos <strong>KIA 2 SERVICIOS</strong> (en adelante, el PLAN 2 SERVICIOS) es un producto del <strong>[ALMACENES SANTA CLARA S.A.]</strong> (en adelante, EL CONCESIONARIO) que le permite al cliente identificado al final del presente documento (en adelante, EL CLIENTE), adquirir en forma anticipada y a un precio fijo y predeterminado, exactamente <strong>2 (dos) servicios de mantenimiento preventivo consecutivos</strong> para su vehículo KIA.</p>
    <p>Los clientes KIA podrán adquirir un Paquete de Mantenimiento KIA 2 SERVICIOS hasta antes de realizar el servicio de <strong>${km1txt} kms</strong> a su vehículo.</p>

    <div class="section-title">2. COBERTURA</div>
    <p>Los servicios comprendidos en cada uno de los Paquetes de Mantenimiento se detallan en el Anexo 1 que se encuentra en la parte final de este documento (en adelante, Anexo 1). Por lo tanto, los servicios que no estén incluidos en el Anexo 1 deberán ser asumidos directamente por EL CLIENTE, pues no forman parte del mismo.</p>

    <div class="section-title">3. PLAN SELECCIONADO</div>
    <table>
      <tr><td class="left" style="padding:5px 8px;border-bottom:1px solid #eee">Plan</td><td style="padding:5px 8px;border-bottom:1px solid #eee"><strong>KIA 2 SERVICIOS</strong></td></tr>
      <tr><td class="left" style="padding:5px 8px;border-bottom:1px solid #eee">Modelo del vehículo</td><td style="padding:5px 8px;border-bottom:1px solid #eee">${modelo}</td></tr>
      <tr><td class="left" style="padding:5px 8px;border-bottom:1px solid #eee">Servicio 1</td><td style="padding:5px 8px;border-bottom:1px solid #eee">${row1}</td></tr>
      <tr><td class="left" style="padding:5px 8px;border-bottom:1px solid #eee">Servicio 2</td><td style="padding:5px 8px;border-bottom:1px solid #eee">${row2}</td></tr>
      <tr><td class="left" style="padding:5px 8px;border-bottom:1px solid #eee">Precio Regular</td><td style="padding:5px 8px;border-bottom:1px solid #eee">${reg} (incluido IGV)</td></tr>
      <tr><td class="left" style="padding:5px 8px"><strong>Precio PPM (con descuento 25%)</strong></td><td style="padding:5px 8px"><strong class="red">${ppm} (incluido IGV)</strong></td></tr>
    </table>

    <div class="section-title">4. VIGENCIA DEL PLAN SELECCIONADO</div>
    <p>La vigencia del PLAN 2 SERVICIOS es de <strong>${vigencia}</strong>, contabilizados desde la realización del primer servicio del plan.</p>

    <div class="section-title">5. CONDICIONES Y RESTRICCIONES</div>
    <ol class="condiciones">
      <li>EL CLIENTE deberá realizar los 2 servicios de mantenimiento únicamente en los talleres de EL CONCESIONARIO donde adquirió el PLAN 2 SERVICIOS.</li>
      <li>Los servicios deben realizarse dentro de los kilometrajes o periodos indicados en el plan seleccionado, lo que ocurra primero.</li>
      <li>En caso EL CLIENTE, dentro del periodo o kilometraje que corresponda, no llegase a realizar uno o varios de los mantenimientos preventivos del paquete que contrató, perderá el derecho a usarlos con posterioridad, toda vez que estos no resultan acumulables. En tales situaciones, tampoco aplicará la devolución de dinero, ni vale de consumo, ni reintegro de cualquier índole respecto de los mantenimientos que EL CLIENTE no hubiese utilizado.</li>
      <li>De la misma forma, no será responsabilidad de EL CONCESIONARIO si EL CLIENTE no hace uso de los servicios de mantenimientos del paquete adquirido dentro de los tiempos o kilometrajes estipulados.</li>
      <li>En caso EL CLIENTE transfiera el Vehículo a un tercero, el nuevo propietario podrá hacer uso de los servicios de mantenimiento preventivo del paquete adquirido por EL CLIENTE. En el supuesto anterior, será exclusiva responsabilidad de EL CLIENTE informar al nuevo propietario sobre los términos y condiciones del Programa, eximiendo a EL CONCESIONARIO y al importador de la marca KIA de toda responsabilidad al respecto.</li>
      <li>EL CLIENTE declara conocer que, para mantener la garantía de producto del Vehículo, deberá realizar los mantenimientos preventivos dentro de la Pauta de Mantenimiento Periódico, tal como se establece en el Manual de Garantía y Mantenimiento del Vehículo. Sin perjuicio de ello, en caso el Vehículo perdiese la garantía de producto, EL CLIENTE podrá seguir haciendo uso de los mantenimientos del paquete contratado.</li>
      <li>El PLAN 2 SERVICIOS adquirido no podrá ser transferido a otro vehículo.</li>
      <li>El PLAN 2 SERVICIOS no incluye mantenimientos correctivos, daños por accidentes, ni servicios adicionales no previstos en la Pauta.</li>
      <li>EL CLIENTE declara que se le ha informado que, en el marco del Plan, EL CONCESIONARIO compartirá sus datos personales con Kia Import Perú S.A.C., con RUC N° 20472468147, importador de la marca KIA.</li>
    </ol>

    <hr>
    <p>Atentamente,</p>
    <p><strong>[ALMACENES SANTA CLARA S.A.]</strong></p>
    <br>
    <p>El presente documento ha sido leído, aprobado y aceptado en todos sus términos por:</p>

    <div class="firma-block">
      <div class="firma-center">
        <div class="firma-line"></div>
        <p><strong>FIRMA DEL CLIENTE</strong></p>
      </div>
    </div>

    <table class="datos-table" style="margin-top:20px">
      <tr><td class="label">Nombre:</td><td>${cliente}</td></tr>
      <tr><td class="label">DNI/RUC del cliente:</td><td><strong>${dni||'—'}</strong></td></tr>
      <tr><td class="label">Fecha:</td><td>${fecha}</td></tr>
      <tr><td class="label">VIN del Vehículo:</td><td><strong>${vin}</strong></td></tr>
    </table>

    <table style="margin-top:16px;border-collapse:collapse;width:100%">
      <tr>
        <td style="border:1px solid #ccc;padding:8px;font-weight:bold;background:#f5f5f5;width:50%">Modelo de Vehículo</td>
        <td style="border:1px solid #ccc;padding:8px">${modelo}</td>
      </tr>
      <tr>
        <td style="border:1px solid #ccc;padding:8px;font-weight:bold;background:#f5f5f5">Plan de Mantenimiento Elegido</td>
        <td style="border:1px solid #ccc;padding:8px">KIA 2 SERVICIOS — <span class="red bold">${ppm} (inc. IGV)</span></td>
      </tr>
    </table>

    <p style="font-size:9pt;color:#666;margin-top:10px">Cotización N° ${cot} · Generado el ${fecha}</p>

    <!-- ANEXO 1 EN PÁGINA SEPARADA -->
    <div style="page-break-before:always;margin-top:10px;padding-top:8px">
      <h2 style="font-size:10pt;font-weight:700;text-align:center;margin-bottom:2px">ANEXO 1</h2>
      <h3 style="font-size:9pt;font-weight:600;text-align:center;margin-bottom:3px">PAUTA DE MANTENIMIENTO PERIÓDICO</h3>
      <p style="font-size:8pt;margin-bottom:3px">Detalle de los servicios incluidos en el <strong>PLAN 2 SERVICIOS — ${km1?kmToLabel(km1):''} + ${km2?kmToLabel(km2):''}</strong> para el vehículo <strong>${modelo}</strong>:</p>
      ${buildAnexoDS(f,km1,km2)}
      ${getRevisionesContratoHTML(modelo,freq,csHasS1,csHasS2,csHasS3,csHasS4)}
    </div>
  </div>`;
}
