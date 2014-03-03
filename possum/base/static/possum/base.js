function date_heure(id) {
        date = new Date;
        h = date.getHours();
        if(h<10)
        {
                h = "0"+h;
        }
        m = date.getMinutes();
        if(m<10)
        {
                m = "0"+m;
        }
        s = date.getSeconds();
        if(s<10)
        {
                s = "0"+s;
        }
        resultat = h+':'+m;
        document.getElementById(id).innerHTML = resultat;
        setTimeout('date_heure("'+id+'");','1000');
        return true;
}

function myLinkButtonClick(clicked_id) {
    var el = document.getElementById("list_"+clicked_id);
    el.style.display = (el.style.display != 'none' ? 'none' : '' );
}

function hide_all_categories() {
    var links = document.getElementsByTagName("div");
    for (var i=0; i<links.length; i++) {
        match = links[i].id.match(/cat_.*$/);
        if (match) {
            links[i].style.display = 'none';
        }
    }
}

function view_category(clicked_id) {
    hide_all_categories();
    var el = document.getElementById("cat_"+clicked_id);
    el.style.display = '';
}
