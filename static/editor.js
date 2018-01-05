var oldvals = [];

function getid(idstr)
{
    // returns correct id for strings of format 'class_id'
    // also returns null for id labelled 'NULL'

    var id = idstr.split("_")[1];
    if(id == "NULL")
    {
        id = null;
    }

    return id;
}

function getparentid(item) {
    // item is the jquery object
    var parent = $($($(item).parent()[0]).children("span")[0]).attr('id');
    var parentid;
    if(parent === void(0)) {
        parentid = 0; // root parent has an id of 0
    } else {
        parentid = parent.split("_")[1];
    }
    return parentid;
}

function toggleEditing(item) {
    // item is the jquery object
    var text = $(item.children()[0]).val();
    var id = getid(item.attr("id"));        
    if(text) {
        // toggle  off        
        if(text != oldvals[id])
        {
            $.ajax({
                url: editurl,
                method: 'POST',
                data: {
                    'id': id,
                    'text': text
                },
                success: function(response) {
                    console.log("Success:\n" + response);
                    item.html(text.replace(/\n/g, "<br/>"));
                },
                error: function(request, error) {
                    console.log("Failure:\n" + error);
                    var textarea = $(item.children("textarea")[0]);
                    textarea.attr("style", "background-color: red");
                }
            });
        }
    } else {
        // toggle on
        oldvals[id] = text;
        item.html("<textarea id='edit_" + id + "' class='form-control editbox'>" + item.text() + "</textarea>");    
        $("#edit_" + id).focus()    
    }
}



$(document).ready(function() {
    $(document).on("click", ".edititem", function(e) {
        e.preventDefault();
        var id = getid(this.id);        
        toggleEditing($("#text_" + id));
    });

    $(document).on("blur", ".editbox", function(e) {
        var id = getid(this.id);                
        toggleEditing($("#text_" + id));
    });

    $(document).on("click", ".additem", function(e) {
        e.preventDefault();
        var id = getid(this.id);
        maxid = maxid + 1;
        var parentid = getparentid(this);
        

        var list = $($($(this).parent()[0]).children("ul")[0]);
        if(list.get(0) === void(0)) {
            if(parentid > 0) {
                $($(this).parents()[0]).append("<ul></ul>");
                list = $($($(this).parent()[0]).children("ul")[0]);
            } else {
                list = $($(this).parent()[0]);
            }
        }        

        $.ajax({
            url: addurl,
            method: 'POST',
            data: {
                'parentid': parentid
            },
            success: function(response) {
                maxid = response;
                var listTemplate = $("<li><span id='text_" + maxid +"'></span> <a href='#' class='edititem' id='edit_" + maxid + "'>edit</a> <a href='#' class='additem' id='add_" + maxid + "'>add</a> <a href='#' class='delitem' id='del_" + maxid + "'>delete</a> <a href='#' class='upitem' id='up_" + maxid + "'>↑</a> <a href='#' class='downitem' id='down_" + maxid + "'>↓</a></li>");
                list.append(listTemplate);
                toggleEditing($("#text_" + maxid));
                console.log(response);
            },
            error: function(request, error) {
                console.log(request);
            }
        });

    });


    $(document).on("click", ".delitem", function(e) {
        e.preventDefault();
        var id = getid(this.id);
        $.ajax({
            url: delurl,
            method: 'POST',
            data: {
                'id': id
            },
            success: function(response) {
                console.log(response);
                $($("#text_" + id).parent()[0]).remove();
            },
            error: function(request, error) {
                console.log("Failure:\n" + error);
            }
        });
    });

    $(document).on("click", ".upitem", function(e) {
        e.preventDefault();
        var id = getid(this.id);
        var parent = $($($($(this).parent()[0]).parent()[0]).parent()[0]).children("span")[0];
        var parentid;
        if(parent === void(0)){
            parentid = 0;
        } else {
            parentid = getid(parent.id);
        }

        $.ajax({
            url: upurl,
            method: 'POST',
            data: {
                'id': id,
                'parentid': parentid
            },
            success: function(response) {
                console.log(response);
                if(response.length > 0) {
                    $($(response).parent()[0]).before($($("#text_" + id).parent()[0]))
                }   
            },
            error: function(request, error) {
                console.log("Failure:\n" + error);
            }
        });
    });

    $(document).on("click", ".downitem", function(e) {
        e.preventDefault();
        var id = getid(this.id);
        var parent = $($($($(this).parent()[0]).parent()[0]).parent()[0]).children("span")[0];
        var parentid;
        if(parent === void(0)){
            parentid = 0;
        } else {
            parentid = getid(parent.id);
        }
        $.ajax({
            url: downurl,
            method: 'POST',
            data: {
                'id': id,
                'parentid': parentid
            },
            success: function(response) {
                console.log(response);
                if(response.length > 0) {
                    $($(response).parent()[0]).after($($("#text_" + id).parent()[0]))
                }
            },
            error: function(request, error) {
                console.log("Failure:\n" + error);
            }
        });
    });

    // auto scrolling textarea
    $(document)
        .on('focus.editbox', 'textarea.editbox', function(){
            var savedValue = this.value;
            this.value = '';
            this.baseScrollHeight = this.scrollHeight;
            this.value = savedValue;
        })
        .on('input.editbox', 'textarea.editbox', function(){
            var minRows = this.getAttribute('data-min-rows')|0, rows;
            this.rows = minRows;
            rows = Math.ceil((this.scrollHeight - this.baseScrollHeight) / 16);
            this.rows = minRows + rows;
        });
});


