$(document).ready(function() {
	$(".sorted-table").tablesorter({
		sortList : [[0, 0]]
	});
});

////////////////////
// CONFIGS EDITOR //
////////////////////

function edit_request(event, config_name) {
	(event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	$.post("", {
		config_name : config_name,
		action : 'edit',
	}, function(data) {
		$('#id_content').html(data);
	});
}

function confirm_save(event, config_name) {
	(event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	var content = $('#id_config_text').val()
	var root_passwd = $('#id_root_passwd').val()
	var c = confirm("Do you realy want to save file " + config_name +"?");
	if (c == true) {
		$.post("", {
			config_name : config_name,
			content : content,
			root_passwd : root_passwd,
			action : 'save',
		}, function(data) {
			if (data == '') {
				window.location.reload();
			} else {
				$('#id_error_div').removeClass('hidden')
				$('#id_error_div').html(data)
			}
		});
	}

}

function confirm_cancel(event) {
	(event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	var c = confirm("Do you really want to discard changes? All changes will be lost!");
	if (c == true) {
		window.location.reload()
	}
}

////////////////
// FILES TREE //
////////////////

function open_folder(event, id, full_name) {
	(event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	
	if ($('#' + id).hasClass('in')) {
		$("#" + id).collapse('hide');
    	$("#" + id + "_img_minus").addClass('hidden')
    	$("#" + id + "_img_plus").removeClass('hidden')
	}
	
	else {
		var onclick = $('#link_' + id).attr('onclick')
		$('#link_' + id).removeAttr('onclick');
		$("#loading_img_" + id).removeClass('hidden');
		$.post("", {
	        full_name : full_name,
	        },function(data) {
	        	$('#' + id).html(data);
	        	$("#" + id).collapse('show');
	        	$("#" + id + "_img_plus").addClass('hidden')
    			$("#" + id + "_img_minus").removeClass('hidden')
    			$("#loading_img_" + id).addClass('hidden')
    			$('#link_' + id).attr('onclick', onclick)
	        }
		);
	}
}

function send_post(event, post_url, full_name, action, is_dir) {
	(event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	$("#loading_info").removeClass('hidden')
	$.post(post_url, {
        full_name : full_name,
        action : action,
        is_dir : is_dir,
        },function(data) {
        	if (data == '') {
        		window.location.reload();
        	}
              $('#get_info_div').html(data);
              $("#loading_info").addClass('hidden')
        }
	);
}
