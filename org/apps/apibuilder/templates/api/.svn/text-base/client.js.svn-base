function show(pk,model,fields){
    document.write('<h2>'+model+' '+pk+'</h2><ul>');
    for (var i in fields){
        document.write('<li><b>'+i+'</b> '+fields[i]+'</li>');
    }
    document.write('</ul>');
}

function api_query(url, data, callback){

    if (callback == undefined)
        callback = show;
    if (data == undefined)
        data = new Object();
    data.format = 'json';
    $.getJSON(url, data, function(json){
        $.each(json, function(i,obj){
            callback(parseInt(obj.pk),obj.model.toString(),new Object(obj.fields));
        });
    });
}