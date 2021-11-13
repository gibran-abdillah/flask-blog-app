var id_addcat = document.getElementById('add_cat')
$('#addcat').click(function() {
    var new_input = document.createElement('input')
    var p = document.createElement('p')
    new_input.name = 'category[]'
    new_input.type = 'text'
    p.appendChild(new_input)
    id_addcat.appendChild(p)
})