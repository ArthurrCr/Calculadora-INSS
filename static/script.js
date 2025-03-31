function addFields() {
    var container = document.getElementById('dynamicFields');
    var originalGroup = container.querySelector('.input-group');
    var newGroup = originalGroup.cloneNode(true);
    
    // Limpa os valores dos campos clonados
    newGroup.querySelectorAll('input, select').forEach(function(input) {
        input.value = '';
    });
    
    // Aplica efeito de fade-in ao novo grupo
    newGroup.style.opacity = 0;
    container.appendChild(newGroup);
    setTimeout(function(){
        newGroup.style.transition = "opacity 0.5s ease-in-out";
        newGroup.style.opacity = 1;
    }, 50);
}
