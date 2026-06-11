/* ===================================================================
   EOD Chile · Movilidad Urbana
   Encuestas Origen-Destino · 18 ciudades homologadas y expandidas
   By Rodrigo Medina González · Universidad de Concepción
   =================================================================== */

// ── Constantes de color ──────────────────────────────────────────────────────
const NAVY="#1f4e79", NAVY2="#2e5e8c", OR="#d96a1f", TEAL="#1f8a86",
      GREEN="#1a9850", RED="#d6453a", GREY="#9aa7b4";

const MODO_COL={
  "Público":       NAVY,
  "Privado":       RED,
  "No motorizado": GREEN,
  "Combinado":     OR,
  "Otro":          GREY
};
const PROP_COL={
  "Trabajo": NAVY,
  "Estudio": TEAL,
  "Otro":    GREY
};
const QUINTIL_COL=["#d73027","#fc8d59","#fee08b","#91cf60","#1a9850"];
const ETARIO_PAL=["#bdc9e1","#74a9cf","#2b8cbe","#1d6fa4","#145888","#0a3a61"];
const TRAMO_PAL={
  "0-1":"#c7e9c0","1-2":"#a1d99b","2-3":"#74c476",
  "3-4":"#41ab5d","4-5":"#238b45","5-6":"#006d2c","6+":"#00441b"
};
const USUARIO_PAL=["#c6dbef","#6baed6","#2171b5","#084594"];

// ── Estado global ────────────────────────────────────────────────────────────
const S={index:[],data:{},sel:null};
const MAPS=[];
const CH={};
let odMap=null, odLyr=null, odInfo=null, odLegend=null;
let mapView="gen";

// ── Utilidades ───────────────────────────────────────────────────────────────
function getJSON(url){
  return fetch(url).then(r=>r.text())
    .then(t=>JSON.parse(t.replace(/\bNaN\b/g,"null").replace(/-?\bInfinity\b/g,"null")));
}

function slugify(s){
  return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")
    .replace(/[^a-z0-9]+/g,"_").replace(/^_|_$/g,"");
}

function fmt(x,d=1){
  if(x==null||!isFinite(x))return "s/d";
  return x.toLocaleString("es-CL",{minimumFractionDigits:d,maximumFractionDigits:d});
}

function fmtM(x){
  if(x==null||!isFinite(x))return "s/d";
  if(x>=1e6)return fmt(x/1e6,1)+"M";
  if(x>=1e3)return fmt(x/1e3,0)+"k";
  return fmt(x,0);
}

function pct(v){
  if(v==null||!isFinite(v))return "s/d";
  return fmt(v,1)+"%";
}

// ── Colores de período horario ───────────────────────────────────────────────
function horaColor(h){
  if(h>=7&&h<9)   return "rgba(31,78,121,.90)";
  if(h>=12&&h<14) return "rgba(217,106,31,.88)";
  if(h>=17&&h<20) return "rgba(31,138,134,.90)";
  return "rgba(94,110,128,.45)";
}

// ── Tema claro / oscuro ──────────────────────────────────────────────────────
const CARTO_LIGHT="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
const CARTO_DARK ="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

function isDark(){return document.documentElement.classList.contains("dark");}

function applyMapTheme(){
  const u=isDark()?CARTO_DARK:CARTO_LIGHT;
  MAPS.forEach(m=>{try{m.carto.setUrl(u);}catch(e){}});
}

function applyChartTheme(){
  if(!window.Chart)return;
  Chart.defaults.color      =isDark()?"#a9c0de":"#5e6e80";
  Chart.defaults.borderColor=isDark()?"rgba(140,165,200,.14)":"rgba(20,40,70,.07)";
}

function rerenderActive(){
  const t=currentTab();
  if(S.sel){
    if(t==="resumen")    renderResumen(S.sel);
    if(t==="movilidad")  renderMovilidad(S.sel);
    if(t==="demografia") renderDemografia(S.sel);
    if(t==="ingreso")    renderIngreso(S.sel);
    if(t==="mapas")      drawMapView(S.sel);
  }
  if(t==="nacional") renderNacional();
}

function setTheme(dark){
  document.documentElement.classList.toggle("dark",dark);
  try{localStorage.setItem("theme",dark?"dark":"light");}catch(e){}
  updateThemeIcon();
  applyChartTheme();
  applyMapTheme();
  rerenderActive();
}

const MOON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
const SUN ='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
function updateThemeIcon(){const b=document.getElementById("themeToggle");if(b)b.innerHTML=isDark()?SUN:MOON;}

// ── Mapa Leaflet — helpers ───────────────────────────────────────────────────
function authorWM(map){
  const c=L.control({position:"bottomleft"});
  c.onAdd=function(){const d=L.DomUtil.create("div","author-wm");d.textContent="By Rodrigo Medina G.";return d;};
  c.addTo(map);return c;
}

function mapChrome(map){
  const claro=L.tileLayer(isDark()?CARTO_DARK:CARTO_LIGHT,
    {attribution:'&copy; OpenStreetMap &copy; CARTO',maxZoom:19});
  const sat=L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {attribution:'Imagery &copy; Esri, Maxar, Earthstar Geographics',maxZoom:19});
  claro.addTo(map);MAPS.push({map,carto:claro});
  L.control.layers({"Mapa":claro,"Satélite":sat},null,{position:"topright"}).addTo(map);
  const fc=L.control({position:"topleft"});
  fc.onAdd=function(){
    const d=L.DomUtil.create("div","leaflet-bar fs-ctrl");
    const a=L.DomUtil.create("a","",d);
    a.href="#";a.title="Pantalla completa";a.setAttribute("role","button");a.setAttribute("aria-label","Pantalla completa");
    a.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3m13-5v3a2 2 0 1-2 2h-3"/></svg>';
    L.DomEvent.on(a,"click",function(e){
      L.DomEvent.stop(e);const el=map.getContainer();
      if(!document.fullscreenElement)(el.requestFullscreen||el.webkitRequestFullscreen||function(){}).call(el);
      else(document.exitFullscreen||document.webkitExitFullscreen||function(){}).call(document);
      setTimeout(()=>map.invalidateSize(),250);
    });
    return d;
  };
  fc.addTo(map);authorWM(map);
  return{claro,sat};
}

// ── Tabs ─────────────────────────────────────────────────────────────────────
function currentTab(){
  const b=document.querySelector(".tabs button.on");return b?b.dataset.tab:"resumen";
}

function activateTab(t){
  document.querySelectorAll(".tabs button").forEach(x=>{
    const on=x.dataset.tab===t;
    x.classList.toggle("on",on);x.setAttribute("aria-selected",on?"true":"false");
  });
  document.querySelectorAll(".panel").forEach(p=>p.classList.toggle("on",p.id==="p-"+t));
  if(t==="mapas"&&odMap)setTimeout(()=>odMap.invalidateSize(),60);
  if(t==="resumen"&&S.sel)    renderResumen(S.sel);
  if(t==="movilidad"&&S.sel)  renderMovilidad(S.sel);
  if(t==="demografia"&&S.sel) renderDemografia(S.sel);
  if(t==="ingreso"&&S.sel)    renderIngreso(S.sel);
  if(t==="mapas"&&S.sel)      renderMapas(S.sel);
  if(t==="nacional")          renderNacional();
  writeURL();
}

document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>activateTab(b.dataset.tab));

(function(){
  const nav=document.querySelector(".tabs");if(!nav)return;
  const btns=[...nav.querySelectorAll("button")];
  nav.addEventListener("keydown",e=>{
    if(e.key!=="ArrowRight"&&e.key!=="ArrowLeft")return;
    const i=btns.indexOf(document.activeElement);if(i<0)return;
    e.preventDefault();
    const n=(i+(e.key==="ArrowRight"?1:btns.length-1)+btns.length)%btns.length;
    btns[n].focus();activateTab(btns[n].dataset.tab);
  });
})();

// ── Deep-linking ─────────────────────────────────────────────────────────────
function writeURL(){
  try{
    const q=new URLSearchParams();
    if(S.sel)q.set("c",S.sel.slug);
    const t=currentTab();if(t&&t!=="resumen")q.set("t",t);
    history.replaceState(null,"",location.pathname+(q.toString()?"?"+q.toString():""));
  }catch(e){}
}

function applyURL(){
  const q=new URLSearchParams(location.search);
  const c=q.get("c"),t=q.get("t");
  const entry=c?S.index.find(e=>e.slug===c):null;
  const slug=entry?entry.slug:(S.index.length?S.index[0].slug:null);
  if(!slug)return;
  loadCity(slug).then(()=>{if(t&&document.getElementById("p-"+t))activateTab(t);});
}

// ── Selector de ciudad ───────────────────────────────────────────────────────
function buildSelector(){
  const sel=document.getElementById("city-sel");
  sel.innerHTML=S.index.map(c=>`<option value="${c.slug}">${c.ciudad} · EOD ${c.anio}</option>`).join("");
  sel.onchange=()=>loadCity(sel.value);
  document.getElementById("htag").textContent=S.index.length+" ciudades · datos SECTRA/MOP homologados";
  buildSidebarList();
}

function buildSidebarList(){
  const list=document.getElementById("city-list");if(!list)return;
  list.innerHTML=S.index.map(c=>{
    const meta=c.pct_publico!=null?`EOD ${c.anio} · ${fmt(c.pct_publico,1)}% púb.`:`EOD ${c.anio}`;
    return `<button class="city-item" data-slug="${c.slug}" onclick="loadCity('${c.slug}');closeSidebarMobile()">
      <span class="cn">${c.ciudad}</span>
      <span class="cm">${meta}</span>
    </button>`;
  }).join("");
}

function updateSidebarActive(slug){
  document.querySelectorAll("#city-list .city-item").forEach(b=>{
    b.classList.toggle("active",b.dataset.slug===slug);
  });
  // Scroll active item into view
  const active=document.querySelector("#city-list .city-item.active");
  if(active)active.scrollIntoView({block:"nearest",behavior:"smooth"});
}

function openSidebarMobile(){
  document.getElementById("sidebar").classList.add("open");
  document.getElementById("sidebarOverlay").classList.add("active");
  document.body.style.overflow="hidden";
}

function closeSidebarMobile(){
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebarOverlay").classList.remove("active");
  document.body.style.overflow="";
}

// ── Carga de ciudad ──────────────────────────────────────────────────────────
function loadCity(slug){
  if(!slug)return Promise.resolve();
  if(S.data[slug]){
    S.sel=S.data[slug];
    document.getElementById("city-sel").value=slug;
    updateSidebarActive(slug);
    render();return Promise.resolve();
  }
  return getJSON("data/eod/"+slug+".json").then(d=>{
    S.data[slug]=d;S.sel=d;
    document.getElementById("city-sel").value=slug;
    updateSidebarActive(slug);
    render();
  }).catch(e=>console.error("Error cargando",slug,e));
}

// ── Render general ───────────────────────────────────────────────────────────
function render(){
  const d=S.sel;if(!d)return;
  document.getElementById("res-title").innerHTML=d.ciudad+'<span class="bar"></span>';
  document.getElementById("res-lead").innerHTML=
    'Encuesta Origen-Destino <b>'+d.anio+'</b> · '+
    d.kpis.total_viajes.toLocaleString("es-CL")+' viajes expandidos en día laboral · '+
    (d.zonas?d.zonas.length:0)+' zonas georeferenciadas.';
  document.getElementById("sel-ctx").innerHTML='<b>'+d.ciudad+'</b> · EOD '+d.anio;
  renderResumen(d);
  const t=currentTab();
  if(t==="movilidad")   renderMovilidad(d);
  else if(t==="demografia") renderDemografia(d);
  else if(t==="ingreso")    renderIngreso(d);
  else if(t==="mapas")      renderMapas(d);
  else if(t==="nacional")   renderNacional();
  writeURL();
}

// ── TAB 1: RESUMEN ────────────────────────────────────────────────────────────
function renderResumen(d){
  const k=d.kpis;

  const topProp=d.proposito&&d.proposito.length?[...d.proposito].sort((a,b)=>b.pct-a.pct)[0]:null;

  let html=`
    <div class="kpi"><div class="v">${fmtM(k.total_viajes)}</div><div class="l">Viajes en día laboral</div><div class="s">viajes expandidos</div></div>
    <div class="kpi"><div class="v">${k.tiempo_medio_min!=null?fmt(k.tiempo_medio_min,0)+" min":"s/d"}</div><div class="l">Tiempo medio de viaje</div><div class="s">minutos por viaje</div></div>
    <div class="kpi"><div class="v" style="color:${NAVY}">${pct(k.pct_publico)}</div><div class="l">Transporte público</div><div class="s">% del total</div></div>
    <div class="kpi"><div class="v" style="color:${RED}">${pct(k.pct_privado)}</div><div class="l">Transporte privado</div><div class="s">automóvil y moto</div></div>
    <div class="kpi"><div class="v" style="color:${GREEN}">${pct(k.pct_no_motorizado)}</div><div class="l">No motorizado</div><div class="s">caminata y bicicleta</div></div>`;

  if(k.dist_mediana!=null)
    html+=`<div class="kpi"><div class="v or">${fmt(k.dist_mediana,1)} km</div><div class="l">Distancia mediana</div><div class="s">centroide a centroide</div></div>`;
  if(k.viajes_persona!=null)
    html+=`<div class="kpi"><div class="v">${fmt(k.viajes_persona,2)}</div><div class="l">Viajes por persona</div><div class="s">viajes / habitante día laboral</div></div>`;
  if(k.viajes_hogar!=null)
    html+=`<div class="kpi"><div class="v">${fmt(k.viajes_hogar,1)}</div><div class="l">Viajes por hogar</div><div class="s">viajes / hogar día laboral</div></div>`;
  if(k.pct_trabajo!=null)
    html+=`<div class="kpi"><div class="v" style="color:${NAVY}">${pct(k.pct_trabajo)}</div><div class="l">Motivo trabajo</div><div class="s">% del total de viajes</div></div>`;
  if(k.pct_estudio!=null)
    html+=`<div class="kpi"><div class="v" style="color:${TEAL}">${pct(k.pct_estudio)}</div><div class="l">Motivo estudio</div><div class="s">% del total de viajes</div></div>`;

  document.getElementById("res-kpis").innerHTML=html;

  // horario total
  if(d.horario&&d.horario.length){
    if(CH.horario)CH.horario.destroy();
    const ctx=document.getElementById("c-horario");if(ctx){
      CH.horario=new Chart(ctx,{
        type:"bar",
        data:{
          labels:d.horario.map(h=>h.h+"h"),
          datasets:[{
            data:d.horario.map(h=>h.pct),
            backgroundColor:d.horario.map(h=>horaColor(h.h)),
            borderWidth:0,borderRadius:3
          }]
        },
        options:{
          maintainAspectRatio:false,
          plugins:{
            legend:{display:false},
            datalabels:{display:false},
            tooltip:{callbacks:{label:c=>c.parsed.y.toFixed(2)+"% de los viajes"}}
          },
          scales:{
            x:{ticks:{font:{size:11}},grid:{display:false}},
            y:{ticks:{callback:v=>v+"%"},grid:{color:"rgba(20,40,70,.05)"}}
          }
        }
      });
    }
  }

  // distancia
  renderDistancia(d);
}

// ── Barras horizontales simples (hBarChart) ──────────────────────────────────
function hBarChart(id,labels,data,colors,unit){
  const ctx=document.getElementById(id);if(!ctx)return;
  if(CH[id])CH[id].destroy();
  if(!labels||!labels.length)return;
  const maxVal=Math.max(...data.filter(v=>v!=null));
  CH[id]=new Chart(ctx,{
    type:"bar",
    data:{labels,datasets:[{data,backgroundColor:colors,borderWidth:0,borderRadius:4}]},
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      layout:{padding:{right:46}},
      plugins:{
        legend:{display:false},
        datalabels:{
          display:true,anchor:"end",align:"end",clamp:true,
          color:isDark()?"#a9c0de":"#5e6e80",
          font:{size:10,weight:"700"},
          formatter:v=>v!=null?fmt(v,1)+unit:""
        },
        tooltip:{callbacks:{label:c=>fmt(c.parsed.x,1)+unit}}
      },
      scales:{
        x:{display:false,max:maxVal*1.22},
        y:{ticks:{font:{size:12}},grid:{display:false}}
      }
    }
  });
}

// ── Barras apiladas horizontales (cross-tabs) ────────────────────────────────
function stackedBar(id,chartData){
  if(!chartData)return;
  const ctx=document.getElementById(id);if(!ctx)return;
  if(CH[id])CH[id].destroy();
  const{labels,datasets}=chartData;
  if(!labels||!datasets||!labels.length)return;
  CH[id]=new Chart(ctx,{
    type:"bar",
    data:{
      labels,
      datasets:datasets.map(ds=>({
        label:ds.label,
        data:ds.data,
        backgroundColor:ds.color||GREY,
        borderWidth:0,
      }))
    },
    options:{
      indexAxis:"y",maintainAspectRatio:false,
      plugins:{
        legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:10,font:{size:11}}},
        datalabels:{
          display:ctx=>{const v=ctx.dataset.data[ctx.dataIndex];return v!=null&&v>=8;},
          anchor:"center",align:"center",
          color:"#fff",
          font:{size:10,weight:"700"},
          formatter:v=>v!=null&&v>=8?Math.round(v)+"%":""
        },
        tooltip:{callbacks:{label:c=>c.dataset.label+": "+fmt(c.parsed.x,1)+"%"}}
      },
      scales:{
        x:{stacked:true,display:false,max:100},
        y:{stacked:true,ticks:{font:{size:11}},grid:{display:false}}
      }
    }
  });
}

// ── Distribución por distancia ────────────────────────────────────────────────
function renderDistancia(d){
  if(!d.distancia||!d.distancia.length)return;
  if(CH["c-distancia"])CH["c-distancia"].destroy();
  const ctx=document.getElementById("c-distancia");if(!ctx)return;
  const maxV=Math.max(...d.distancia.map(t=>t.pct||0));
  CH["c-distancia"]=new Chart(ctx,{
    type:"bar",
    data:{
      labels:d.distancia.map(t=>t.tramo+" km"),
      datasets:[{
        data:d.distancia.map(t=>t.pct),
        backgroundColor:d.distancia.map(t=>TRAMO_PAL[t.tramo]||"#41ab5d"),
        borderWidth:0,borderRadius:3,
      }]
    },
    options:{
      maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        datalabels:{
          display:true,anchor:"end",align:"end",clamp:true,
          color:isDark()?"#a9c0de":"#5e6e80",
          font:{size:10,weight:"700"},
          formatter:v=>v>0.5?fmt(v,1)+"%":""
        },
        tooltip:{callbacks:{label:c=>c.parsed.y.toFixed(1)+"% de los viajes"}}
      },
      scales:{
        x:{ticks:{font:{size:11}},grid:{display:false}},
        y:{display:false,max:maxV*1.3}
      }
    }
  });
}

// ── TAB 2: MODOS ─────────────────────────────────────────────────────────────
function renderMovilidad(d){
  renderModal(d);renderProp(d);renderEtario(d);renderQuintil(d);
  renderHorarioModal(d);renderPropModo(d);
}

function renderModal(d){
  if(!d.modal||!d.modal.length)return;
  hBarChart("c-modal",d.modal.map(m=>m.modo),d.modal.map(m=>m.pct),
    d.modal.map(m=>MODO_COL[m.modo]||GREY),"%");
}
function renderProp(d){
  if(!d.proposito||!d.proposito.length)return;
  hBarChart("c-prop",d.proposito.map(p=>p.prop),d.proposito.map(p=>p.pct),
    d.proposito.map(p=>PROP_COL[p.prop]||GREY),"%");
}
function renderEtario(d){
  if(!d.etario||!d.etario.length)return;
  hBarChart("c-etario",d.etario.map(e=>e.grupo),d.etario.map(e=>e.pct),
    d.etario.map((_,i)=>ETARIO_PAL[i]||NAVY),"%");
}
function renderQuintil(d){
  if(!d.quintil||!d.quintil.length)return;
  hBarChart("c-quintil",
    d.quintil.map(q=>"Q"+q.q+" · "+(["Bajo","Medio-bajo","Medio","Medio-alto","Alto"][q.q-1]||"")),
    d.quintil.map(q=>q.pct),QUINTIL_COL,"%");
}

function renderHorarioModal(d){
  if(!d.horario_modal)return;
  if(CH["c-horario-modal"])CH["c-horario-modal"].destroy();
  const ctx=document.getElementById("c-horario-modal");if(!ctx)return;
  const{labels,datasets}=d.horario_modal;
  CH["c-horario-modal"]=new Chart(ctx,{
    type:"bar",
    data:{
      labels,
      datasets:datasets.map(ds=>({
        label:ds.label,data:ds.data,
        backgroundColor:ds.color,borderWidth:0,
      }))
    },
    options:{
      maintainAspectRatio:false,
      plugins:{
        legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:8,padding:12,font:{size:11}}},
        datalabels:{display:false},
        tooltip:{callbacks:{label:c=>c.dataset.label+": "+c.parsed.y.toFixed(2)+"% del día"}}
      },
      scales:{
        x:{stacked:true,ticks:{font:{size:10}},grid:{display:false}},
        y:{stacked:true,ticks:{callback:v=>v+"%",font:{size:10}},grid:{color:"rgba(20,40,70,.05)"}}
      }
    }
  });
}

function renderPropModo(d){
  if(!d.prop_modo)return;
  stackedBar("c-prop-modo",d.prop_modo);
}

// ── TAB 3: DEMOGRAFÍA ────────────────────────────────────────────────────────
function renderDemografia(d){
  if(d.tipo_usuario&&d.tipo_usuario.length){
    hBarChart("c-tipo-usuario",
      d.tipo_usuario.map(u=>u.tipo),
      d.tipo_usuario.map(u=>u.pct),
      USUARIO_PAL.slice(0,d.tipo_usuario.length),"%");
  }
  stackedBar("c-modal-etario",d.modal_etario);
  stackedBar("c-modal-usuario",d.modal_usuario);
  stackedBar("c-prop-etario",d.prop_etario);
}

// ── TAB 4: INGRESO ───────────────────────────────────────────────────────────
function renderIngreso(d){
  stackedBar("c-modal-quintil",d.modal_quintil);
  stackedBar("c-dist-quintil",d.dist_quintil);
  stackedBar("c-dist-modo",d.dist_modo);
}

// ── TAB 5: MAPAS OD ──────────────────────────────────────────────────────────
const MAP_DESC={
  gen:"Viajes <b>generados</b> por zona (salidas desde el origen). Círculos anaranjados proporcionales al volumen.",
  atr:"Viajes <b>atraídos</b> por zona (llegadas al destino). Círculos azules proporcionales al volumen.",
  od :"Top 150 pares OD por volumen. Líneas de deseo entre origen y destino; grosor proporcional al flujo."
};
const MAP_NOTE={
  gen:"Fuente: EOD procesada. Círculos proporcionales al volumen de viajes generado (factor de expansión).",
  atr:"Fuente: EOD procesada. Círculos proporcionales al volumen de viajes atraído (factor de expansión).",
  od :"Top 150 pares OD por volumen de viajes expandidos. Las líneas son de deseo — no representan rutas reales."
};

document.querySelectorAll(".ctrl button[data-view]").forEach(b=>
  b.onclick=()=>setMapView(b.dataset.view));

function setMapView(v){
  mapView=v;
  document.querySelectorAll(".ctrl button[data-view]").forEach(b=>b.classList.toggle("on",b.dataset.view===v));
  document.getElementById("map-desc").innerHTML=MAP_DESC[v];
  document.getElementById("map-note").textContent=MAP_NOTE[v];
  if(S.sel)drawMapView(S.sel);
}

function ensureOdMap(){
  if(odMap)return;
  odMap=L.map("od-map",{preferCanvas:true}).setView([-33.5,-70.7],11);
  mapChrome(odMap);
  odInfo=L.control({position:"topright"});
  odInfo.onAdd=function(){this._d=L.DomUtil.create("div","info");this._d.innerHTML="<b>Pasa el cursor</b><br>sobre una zona";return this._d;};
  odInfo.update=function(html){this._d.innerHTML=html||"<b>Pasa el cursor</b><br>sobre una zona";};
  odInfo.addTo(odMap);
  odLegend=L.control({position:"bottomright"});
  odLegend.onAdd=function(){this._d=L.DomUtil.create("div","legend");return this._d;};
  odLegend.addTo(odMap);
}

function drawMapView(d){
  ensureOdMap();
  if(odLyr){odMap.removeLayer(odLyr);odLyr=null;}
  odInfo.update(null);
  if(mapView==="gen"||mapView==="atr")drawCircles(d,mapView);
  else drawODLines(d);
}

function drawCircles(d,view){
  const zones=d.zonas;
  if(!zones||!zones.length){odInfo.update("Sin datos de zonas.");return;}
  const vals=zones.map(z=>view==="gen"?z.gen:z.atr);
  const maxVal=Math.max(...vals)||1;
  const color=view==="gen"?OR:NAVY;
  const lbl=view==="gen"?"Generación":"Atracción";
  const lyr=L.layerGroup();
  zones.forEach(z=>{
    const val=view==="gen"?z.gen:z.atr;if(!val)return;
    const r=4+Math.sqrt(val/maxVal)*22;
    const m=L.circleMarker([z.lat,z.lng],{
      radius:r,color:"rgba(255,255,255,.55)",weight:1,
      fillColor:color,fillOpacity:0.72
    });
    m.on("mouseover",()=>{
      m.setStyle({fillOpacity:.92,weight:2});
      odInfo.update(`<b>Zona ${z.zona}</b><br>${lbl}:<br><b>${val.toLocaleString("es-CL")} viajes</b><br><small>Gen: ${z.gen.toLocaleString("es-CL")} · Atr: ${z.atr.toLocaleString("es-CL")}</small>`);
    });
    m.on("mouseout",()=>{m.setStyle({fillOpacity:.72,weight:1});odInfo.update(null);});
    m.bindPopup(`<b>Zona ${z.zona}</b><br>${lbl}: <b>${val.toLocaleString("es-CL")} viajes</b>`);
    lyr.addLayer(m);
  });
  lyr.addTo(odMap);odLyr=lyr;
  odLegend._d.innerHTML='<b>'+lbl+'</b>'+
    [["8","Bajo","0.4"],["14","Medio","0.65"],["20","Alto","0.85"]].map(([sz,lab,op])=>
      `<div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="display:inline-block;width:${sz}px;height:${sz}px;border-radius:50%;background:${color};opacity:${op}"></span>${lab}
      </div>`).join("");
  const pts=zones.filter(z=>(view==="gen"?z.gen:z.atr)>0).map(z=>[z.lat,z.lng]);
  if(pts.length)odMap.fitBounds(L.latLngBounds(pts).pad(0.1));
}

function drawODLines(d){
  const flows=d.od_top;
  if(!flows||!flows.length){odInfo.update("Sin datos de flujos OD.");return;}
  const maxN=Math.max(...flows.map(f=>f.n))||1;
  const lyr=L.layerGroup();
  flows.forEach(f=>{
    const w=0.8+Math.sqrt(f.n/maxN)*5.5;
    const op=0.18+(f.n/maxN)*0.68;
    const line=L.polyline([[f.olat,f.olng],[f.dlat,f.dlng]],{color:NAVY2,weight:w,opacity:op});
    line.on("mouseover",()=>{
      line.setStyle({color:OR,opacity:Math.min(op+0.3,1),weight:w+1.5});
      odInfo.update(`<b>Zona ${f.o} → ${f.d}</b><br>Flujo: <b>${f.n.toLocaleString("es-CL")} viajes</b>`);
    });
    line.on("mouseout",()=>{line.setStyle({color:NAVY2,opacity:op,weight:w});odInfo.update(null);});
    line.bindPopup(`<b>${f.o} → ${f.d}</b><br>${f.n.toLocaleString("es-CL")} viajes`);
    lyr.addLayer(line);
  });
  lyr.addTo(odMap);odLyr=lyr;
  odLegend._d.innerHTML='<b>Flujos OD</b>'+
    [["2","Bajo","0.25"],["5","Medio","0.55"],["8","Alto","0.85"]].map(([h,lab,op])=>
      `<div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="display:inline-block;width:26px;height:${h}px;background:${NAVY2};opacity:${op};border-radius:2px"></span>${lab}
      </div>`).join("");
  const pts=flows.flatMap(f=>[[f.olat,f.olng],[f.dlat,f.dlng]]);
  if(pts.length)odMap.fitBounds(L.latLngBounds(pts).pad(0.08));
}

function renderMapas(d){
  ensureOdMap();
  setTimeout(()=>{odMap.invalidateSize();drawMapView(d);},80);
}

// ── TAB 6: NACIONAL ──────────────────────────────────────────────────────────
function renderNacional(){
  const nacKpis=document.getElementById("nac-kpis");
  if(nacKpis&&S.index.length){
    const totalV=S.index.reduce((a,c)=>a+(c.viajes||0),0);
    const pubList=S.index.filter(c=>c.pct_publico!=null);
    const avgPub=pubList.length?pubList.reduce((a,c)=>a+c.pct_publico,0)/pubList.length:null;
    const dmList=S.index.filter(c=>c.dist_mediana!=null);
    const avgDm=dmList.length?dmList.reduce((a,c)=>a+c.dist_mediana,0)/dmList.length:null;
    nacKpis.innerHTML=`
      <div class="kpi"><div class="v">${S.index.length}</div><div class="l">Ciudades cubiertas</div><div class="s">EOD homologadas</div></div>
      <div class="kpi"><div class="v">${fmtM(totalV)}</div><div class="l">Viajes expandidos</div><div class="s">suma 18 ciudades día laboral</div></div>
      <div class="kpi"><div class="v" style="color:${NAVY}">${avgPub!=null?fmt(avgPub,1)+"%":"s/d"}</div><div class="l">% Público promedio</div><div class="s">promedio simple entre ciudades</div></div>
      <div class="kpi"><div class="v or">${avgDm!=null?fmt(avgDm,1)+" km":"s/d"}</div><div class="l">Dist. mediana promedio</div><div class="s">centroide a centroide</div></div>`;
  }

  const nacTable=document.getElementById("nac-table");
  if(!nacTable||!S.index.length)return;
  const rows=S.index.map(c=>{
    const sel=S.sel&&S.sel.slug===c.slug;
    return `<tr class="${sel?"nac-sel":""}" onclick="loadCity('${c.slug}');activateTab('resumen')" title="Ver ${c.ciudad}">
      <td>${c.ciudad}</td>
      <td class="num">${c.anio}</td>
      <td class="num">${fmtM(c.viajes)}</td>
      <td class="num pub-col">${c.pct_publico!=null?fmt(c.pct_publico,1)+"%":"—"}</td>
      <td class="num">${c.dist_mediana!=null?fmt(c.dist_mediana,1)+" km":"—"}</td>
      <td class="num">${c.viajes_persona!=null?fmt(c.viajes_persona,2):"—"}</td>
    </tr>`;
  }).join("");
  nacTable.innerHTML=`<table class="nac-tbl">
    <thead><tr>
      <th>Ciudad</th>
      <th class="num">Año EOD</th>
      <th class="num">Viajes/día</th>
      <th class="num pub-col">% Público</th>
      <th class="num">Dist. mediana</th>
      <th class="num">V/persona</th>
    </tr></thead>
    <tbody>${rows}</tbody>
  </table>`;
}

// ── Botón compartir ──────────────────────────────────────────────────────────
const SHARE_SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>';
const CHECK_SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';

function doShare(){
  try{
    navigator.clipboard.writeText(location.href).then(()=>{
      const bd=document.getElementById("shareBtnD");
      const bm=document.getElementById("shareBtn");
      if(bd){bd.innerHTML=CHECK_SVG;setTimeout(()=>{bd.innerHTML=SHARE_SVG;},1800);}
      if(bm){bm.innerHTML=SHARE_SVG+' ¡Copiado!';setTimeout(()=>{bm.innerHTML=SHARE_SVG+' Compartir vista';},1800);}
    });
  }catch(e){prompt("Copia este enlace:",location.href);}
}

document.getElementById("shareBtn").onclick=doShare;
const _sbd=document.getElementById("shareBtnD");
if(_sbd)_sbd.onclick=doShare;

// ── Inicialización ───────────────────────────────────────────────────────────
updateThemeIcon();
document.getElementById("themeToggle").onclick=()=>setTheme(!isDark());
document.getElementById("sidebarToggle").onclick=openSidebarMobile;
document.getElementById("sidebarClose").onclick=closeSidebarMobile;
document.getElementById("sidebarOverlay").onclick=closeSidebarMobile;

getJSON("data/eod/index.json").then(idx=>{
  S.index=idx.ciudades;
  buildSelector();
  applyURL();
  // Render national tab if it starts active
  if(currentTab()==="nacional")renderNacional();
}).catch(e=>{
  console.error("No se pudo cargar el índice EOD:",e);
  const main=document.querySelector("main");
  if(main)main.insertAdjacentHTML("afterbegin",
    '<div class="loading">No se pudieron cargar los datos. Verifica que existe <code>data/eod/index.json</code>.</div>');
});
