var konten = document.getElementById('content')
var body_blog = document.getElementById('body_blog')
var page_blog = document.getElementById('pagy')
var id_paginate = document.getElementById('paginate_blog')
var cat_id = document.getElementById('category')


function create_tag(tag_name, class_name){
    let element = document.createElement(tag_name)
    if(class_name.length != 0){
        element.className = class_name
    }
    return element
}


async function put_blog(){
    let response = await fetch('/api/recent-blogs');
    let json_result = await response.json();

    if (json_result['status'] == 'success'){
        for(var key in json_result['data']){

            let data = json_result['data'][key]

            let created_at = data['created_at']
            let thumbnail = '/static/img/' + data['thumbnail']
            let title = data['title']
            let preview = data['preview']

            var wrapper = create_tag(tag_name='div', 'col-lg-4 col-md-6');
            
            var card = create_tag('div', 'card mb-5 shadow')
            var card_image = create_tag('img', 'card-img-top')
            var card_body = create_tag('div', 'card-body')
            var card_text = create_tag('p', 'card-text')
            var card_title = create_tag('b', 'card-title mb-2')
            var card_link = create_tag('a', 'btn btn-outline-success')
            
            card_image.src = thumbnail
            card_link.innerHTML = 'Read More'
            card_link.href = '/blog/' + data['slug']
            card_text.innerHTML = preview
            card_title.innerHTML = title
        
            card_body.appendChild(card_title)
            card_body.appendChild(card_text)
            card_body.appendChild(card_link)

            card.appendChild(card_image)
            card.appendChild(card_body)
            wrapper.appendChild(card)
            konten.appendChild(wrapper)   
        }       
    }
}

async function show_blog(slug) {
    var get_api = await fetch('/api' + slug)
    var json_response = await get_api.json()
    if(json_response['status'] == 'success') {
        let data = await json_response['data']
        let title = data['title']
        let content = data['content']
        let thumbnail_uri = data['thumbnail_url']

        var wrapper = create_tag('div', 'col-md-10 mt-5')
        var title_wrapper = create_tag('div', 'title-post mb-5 text-center')
        var title_h1 = create_tag('h1','')
        var img = create_tag('img', 'img-fluid mb-5 rounded')
        var content_wrapper = create_tag('div', 'blog-content')

        img.src = thumbnail_uri
        title_h1.innerHTML = title 
        title_wrapper.appendChild(title_h1)
        content_wrapper.innerHTML = content 

        wrapper.appendChild(title_wrapper)
        wrapper.appendChild(img)
        wrapper.appendChild(content_wrapper)

        body_blog.appendChild(wrapper)

    }
}


function show_password(){
    var password = document.getElementsByName('input')
    if (password.type == 'password') {
        password.type = 'text'
    }
}

$('#show_password').click(function() {
    var pw = document.getElementById('password')
    var conf_pw = document.getElementById('password_confirmation')
    if (pw.type == 'password' && conf_pw.type == 'password'){
        pw.type = 'text'
        conf_pw.type = 'text'
    }else{
        pw.type = 'password'
        conf_pw.type = 'password'
    }

})

$('#resetpassword').click(function (){
    var email_reset = $('#email_reset').val()
    $.post('/api/reset-password', 
        {email: email_reset},
        function(data, status){
            alert(data['data']);
        }
    )
})



function show_paginate(response_json) {
    var items = response_json['items']
    if(items){
        items.map(function(result) {

            var title = result['title']
            var preview = result['preview']
            var image = '/static/img/' + result['thumbnail']
            var slug = result['slug']

            var wrapper = create_tag('div', 'col-md-6 col-lg-4')
            var card = create_tag('div', 'card mb-5 shadow')
            var img = create_tag('img', 'card-img-top')
            var card_body = create_tag('div', 'card-body')
            var card_title = create_tag('b', 'card-title mb-2')
            var card_text = create_tag('p', 'card-text')
            var read_more = create_tag('a', 'btn btn-outline-success')

            img.src = image 
            card_title.innerHTML = title 
            card_text.innerHTML = preview
            read_more.href = '/blog/' + slug 
            read_more.innerHTML = 'Read More'

            card_body.appendChild(card_title)
            card_body.appendChild(card_text)
            card_body.appendChild(read_more)

            card.appendChild(img)
            card.appendChild(card_body)
            wrapper.appendChild(card)
            id_paginate.appendChild(wrapper)
        })
    }
}

async function paginate_blog(page, prev_id, category){
    if (category.length == 0) {
        var api_paginate = '/api/blogs/page/' + page + '?prev_id=' + prev_id
    }else{
        var api_paginate = '/api/blogs/page/' + page + '?prev_id=' + prev_id + '&category=' + category
    }
    var response = await fetch(api_paginate)
    var response_json = await response.json()
    if(response_json['has_next']) { 
        var next_id = await response_json['next_id']
        show_paginate(response_json)
        return next_id
    }
    show_paginate(response_json)
    document.getElementById('touch_paginate').style.display = 'none'
    return false 
}

$('#touch_paginate').click(function() {
    if(prev_id) {
        if(cat_id) {
            more_blog = paginate_blog(2, prev_id, location.pathname.split('/')[3])
        }else{
            more_blog = paginate_blog(2, prev_id, '')
        }
        more_blog.then(result =>
            prev_id = result
        )
        console.log(prev_id)
    }
})
if(body_blog) {
    show_blog(location.pathname)
}
if(page_blog) {
    if(cat_id) {
        var blogy = paginate_blog('1','1',location.pathname.split('/')[3])
    }else{
        var blogy = paginate_blog('1','1','')
    }
    blogy.then(function(result) {
        prev_id = result
        }
    )
}


if(location.pathname == '/') {
    put_blog();
}