/* script.js - interações leves sem jQuery */

// ====== NAV: marcar link ativo pelo path (fallback, caso esqueça a classe no HTML) ======
(function markActiveNav() {
  var links = document.querySelectorAll('.main-nav a');
  var here = location.pathname.split('/').pop() || 'index.html';
  links.forEach(function(a){
    var href = a.getAttribute('href');
    if (href === here) a.classList.add('active');
  });
})();

(function mapaEstados(){
  var map = document.getElementById('map');
  var select = document.getElementById('seletory');

  function activateState(stateCode){
    // desativa tudo
    document.querySelectorAll('#map .state').forEach(function(el){ el.classList.remove('active'); });
    document.querySelectorAll('.parca .estado').forEach(function(el){ el.classList.remove('active'); });

    if(!stateCode) return;

    var st = document.getElementById('state_' + stateCode);
    var box = document.getElementById('box_' + stateCode);

    if (st) st.classList.add('active');
    if (box) box.classList.add('active');
    if (select) select.value = stateCode;
  }

  if (map){
    map.querySelectorAll('.state').forEach(function(el){
      el.addEventListener('click', function(e){
        e.preventDefault();
        var code = el.getAttribute('data-state');
        activateState(code);
      });
    });
  }

  if (select){
    select.addEventListener('change', function(){
      activateState(select.value);
    });
  }

  // estado inicial (ajuste se quiser outro)
  if (map || select) activateState('mg');
})();


