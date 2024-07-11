$(document).ready(function () {

	//$(".all-operation-table").stupidtable();
	//----- usefull (construct event that can be calle like $(xxx).rightclick) -------
	(function($) {
        $.fn.rightClick = function(method) {
            $(this).bind('contextmenu rightclick', function(e) {
                e.preventDefault();
                if (method && $.isFunction(method)) {
                    method(e);
                }
            })

            };
    })(jQuery);
    //----------------------
	$( ".btn-click-before" ).click(function() {
		$(".form-lg").addClass('width-lg');
	});
	$( ".btn-click-after" ).click(function() {
		$(".form-lg").removeClass('width-lg');
	});
	progress_bar = document.getElementById("progress-bar");
	if ($('.percent-progress-bar').val() !== '') {
		progress_bar.setAttribute("style", 'width:'+parseInt($('.percent-progress-bar').val())+'%;');
	};

    var header = document.getElementById("collapse_menu");
	var btns = header.getElementsByClassName("link-menu");

	for (var i = 0; i < btns.length; i++) {
	  btns[i].addEventListener("click", function() {
	    var current = document.getElementsByClassName("active");
	    current[0].className = current[0].className.replace(" active", "");
	    this.className += " active";
	  });
	};
	$("#all-campaigns").click();
	$("#all-campaigns").addClass("active");

    updateCampaignAction = function(operation, type, value) {
         $.ajax({
            dataType: 'json',
            url: '/operation/update/campaign_action/' + operation + '/' + type + '/' + value,
            type: 'POST',
            proccessData: false,
            data: {},
            }).then(function(records) {
                var data = records.reduce(function(a, b) {
                    a.push({id: b['id']});
                    return a;
                }, []);
               	location.reload();
		});	  
    };	
    campaign_ = document.getElementById("campaign");
    if (campaign_){
            campaign_.addEventListener("drop", function(event) {
            event.preventDefault();
            var data = event.dataTransfer.getData("text");
            if (event.target.nextElementSibling.classList && event.target.nextElementSibling.classList[1] === "badge-campaign-info") {
                updateCampaignAction(parseInt(data), 'campaign', parseInt(event.target.parentElement.attributes.id.value));
            }
            else if (event.target.nextElementSibling.classList[1] === "badge-action-info") {
                updateCampaignAction(parseInt(data), 'action', parseInt(event.target.offsetParent.attributes.id.value));
            }
            return true
        }, false);

        campaign_.addEventListener("dragover", function(event) {
            event.preventDefault();
        }, false);
    }

    function mouseOverOps(operations){
        for (var i = 0; i < operations.length; i++) {
            if (operations[i].attributes.deleted.value === 'not deleted'){
                operations[i].addEventListener("dragstart", function(event){
                    event.dataTransfer.setData("text", (event.target.id).replace('operation',''));

                });
            }
            operations[i].addEventListener("mouseover", function() {
			var current = document.getElementsByClassName("active");
			//if (!current[0].classList.contains('page-item') && !current[0].classList.contains('-liste') )
			    //current[0].className = current[0].className.replace(" active", "");
			$('.ligne-operation').removeClass('active');
            this.className += " active";

	        $('.operation-selected').addClass('display-liste');
	        $('.operation-texte').addClass('display-liste-none');

	        $( ".active .edit-ico" ).click(function() {
				$(".active .ico-modif").removeClass('hidden');
				$(".active .edit-ico").addClass('hidden');
				$('.active .edit-value').removeClass('hidden');
				$('.active .qty-extracted-value').addClass('hidden');
				if (current[0].hasAttribute('volume')) {
					$('.active .edit-value')[0].value = this.attributes.volume.value;
				}
				else {
					$('.active .edit-value')[0].value = '';
					$('.active .edit-value')[0].focus();
				}
			});

			$('.active .edit-value').on("keyup", function(e) {
	        if (e.key === "Enter") {
		        $.ajax({
		            dataType: 'json',
		            url: '/operation/update/' + parseInt((this.attributes.id.value).replace('operation','')) + '/' + 'update' + '/' + parseInt($('.active .edit-value').val()),
		            type: 'POST',
		            proccessData: false,
		            data: {},
		            }).then(function(records) {
		                var data = records.reduce(function(a, b) {
		                    a.push({id: b['id']});
		                    return a;
		                }, []);
		                if (data[0].id !== null) {
							$('.active .qty-extracted-value').html($('.active .edit-value').val());
							location.reload();
		                };
				});
	        }
	        });

            $(".active .ico-info").click(function() {
				$(".active .edit-ico").removeClass('hidden');
				$(".active .ico-modif").addClass('hidden');
				$('.active .edit-value').addClass('hidden');
				$('.active .qty-extracted-value').removeClass('hidden');
				$.ajax({
		            dataType: 'json',
		            url: '/operation/message/list/' + parseInt((this.attributes.id.value).replace('operation','')),
		            type: 'POST',
		            proccessData: false,
		            data: {},
		            }).then(function(res) {
						var op_messages = document.getElementById('op_messages');
						var modal_dialog = $('#operation_info_modal');
						var modal_restricted_access = $('#operation_restricted_access_modal');
						op_messages.innerHTML = "";
						if (res[0] !== undefined && res[0] !== null) {
							if (res[0].length > 0) {

								for (var i = 0; i < res[0].length; i++) {
									var line_doc = document.createElement('tr');
		                            line_doc.setAttribute("class" , "test");
									var doc_author = document.createElement('td');
									var doc_body = document.createElement('td');
									var doc_date = document.createElement('td');
									doc_author.innerHTML =  res[0][i]['author'];
									doc_body.innerHTML =  res[0][i]['body'];
									doc_date.innerHTML =  res[0][i]['date'];
									line_doc.appendChild(doc_author);
									line_doc.appendChild(doc_body);
									line_doc.appendChild(doc_date);
									op_messages.appendChild(line_doc);
								};
		                        modal_dialog.modal('show');
							};
						};
				});
            });

            $(".active .maas-ico-blanc").click(function() {
				$(".active .edit-ico").removeClass('hidden');
				$(".active .ico-modif").addClass('hidden');
				$('.active .edit-value').addClass('hidden');
				$('.active .qty-extracted-value').removeClass('hidden');
				$.ajax({
		            dataType: 'json',
		            url: '/report/' + parseInt((this.attributes.id.value).replace('operation','')) + '/sale_operation',
		            type: 'POST',
		            proccessData: false,
		            data: {},
		            }).then(function(records) {
		            	var data = records.reduce(function(a, b) {
		                    a.push({id: b['id'], report_bi_src: b['report_bi_src'],});
		                    return a;
		                }, []);
					var iframe = document.getElementById('report_bi_src');
					var modal_restricted_access = $('#report_bi_iframe');
					$(iframe).attr('srcdoc', data[0]['report_bi_src']);
					$('.close-report')[0].value = parseInt(data[0]['id']);
                    modal_restricted_access.modal('show');
				});
            });

	        $.ajax({
	            dataType: 'json',
	            url: '/operation/detail/' + parseInt((this.attributes['id'].value).replace('operation','')),
	            type: 'POST',
	            proccessData: false,
	            data: {},
	            }).then(function(records) {
	                var data = records.reduce(function(a, b) {
	                    a.push({searched_profile_desc: b['searched_profile_desc'],
	                            population_scored_desc: b['population_scored_desc'],
	                            name: b['name'],
	                            campaign_id: b['campaign_id'],
	                            action_id: b['action_id'],
	                            searched_profile_count:b['searched_profile_count'],
	                            population_scored_count: b['population_scored_count'],
	                            });
	                    return a;
	                }, []);

	        		self.$(".title-selected").text(data[0]['name']);
	        		if (data[0]['campaign_id'] !== false && data[0]['action_id'] !== false){
	        		    self.$(".campaign-action-selected").text(data[0]['campaign_id'] + " - " +data[0]['action_id']);
	        		}
	        		else if (data[0]['campaign_id'] !== false && data[0]['action_id'] === false){
	        		    self.$(".campaign-action-selected").text(data[0]['campaign_id']);
	        		}
	        		else if (data[0]['campaign_id'] === false && data[0]['action_id'] !== false){
	        		    self.$(".campaign-action-selected").text(data[0]['action_id']);
	        		}
	        		else{
	        		     self.$(".campaign-action-selected").text("");
	        		}
	        		if (data[0]['searched_profile_count'] !== false){
	        		    self.$(".searched_profile_count").text(data[0]['searched_profile_count']);
	        		}
	        		else{
	        		    self.$(".searched_profile_count").text("");
	        		}
	        		if (data[0]['population_scored_count'] !== false){
	        		    self.$(".population_scored_count").text(data[0]['population_scored_count']);
	        		}
	        		else{
                        self.$(".population_scored_count").text("");
	        		}
	        		if (data[0]['searched_profile_desc'] !== false) {
		        		self.$(".searched-profile").text(data[0]['searched_profile_desc']);
	        		}
	        		else {
	        			self.$(".searched-profile").text("");
	        		};
	        		if (data[0]['population_scored_desc'] !== false) {
		        		self.$(".population-scored").text(data[0]['population_scored_desc']);
		        	}
		        	else {
		        		self.$(".population-scored").text("");
		        	};
	            });

			});
		};
	};

    var opContainer = document.getElementById("sale-operation");
    if(opContainer){
        var operations = opContainer.getElementsByClassName("ligne-operation");
        mouseOverOps(operations);
    }


	$(".pbi-iframe").click(function(e) {
        $.ajax({
            dataType: 'json',
            url: '/close/report/' + parseInt($('.close-report').val()),
            type: 'POST',
            proccessData: false,
            data: {},
            }).then(function(records) {
                var data = records.reduce(function(a, b) {
                    a.push({id: b['id']});
                    return a;
                }, []);
            if (data[0]['id']) {
                var modal_restricted_access = $('#report_bi_iframe');
                modal_restricted_access.modal('hide');
            }
        });
	});


    $('#use_available_identifiers')
    .on('change', function() {
        if ($(this).val() === 'on') {
            var next_level = document.getElementById("go_to_the_next_level");
            var request_validate = document.getElementById("request_for_validation");
            if(next_level !== null){
                next_level.checked = false;
            }
            if(request_validate !== null){
                request_validate.checked = false;
            }
        }
    });

    deleteCampaignAction = function(type, value) {
        $.ajax({
            dataType: 'json',
            url: '/' + type + '/delete/' + parseInt(value),
            type: 'POST',
            proccessData: false,
            data: {},
            }).then(function(records) {
                var data = records.reduce(function(a, b) {
                    a.push({unlink: b['unlink'],
                    });
                    return a;
                }, []);
                if (data[0].unlink === true) {
                    location.reload();
                }
        });
    };

    $('#go_to_the_next_level')
    .on('change', function() {
        if ($(this).val() === 'on') {
            document.getElementById("use_available_identifiers").checked = false;
            var request_validate = document.getElementById("request_for_validation");
            if(request_validate !== null){
                request_validate.checked = false;
            }
        }
    });
    $('#request_for_validation')
    .on('change', function() {
        if ($(this).val() === 'on') {
            document.getElementById("use_available_identifiers").checked = false;
            var next_level = document.getElementById("go_to_the_next_level");
            if(next_level !== null){
                next_level.checked = false;
            }
        }
    });

    getActive = function() {
    	var done = [];
    	if (searched_profile_inactive !== null) {
	        if (searched_profile_inactive.src.indexOf("inactif") !== -1) {
	            done.push(population_scored_inactive.src.indexOf("inactif"));
	        }
	        if (population_scored_inactive.src.indexOf("inactif") !== -1) {
	        	done.push(searched_profile_inactive.src.indexOf("inactif"));
	        };
	        if (campaign_inactive.src.indexOf("inactif") !== -1) {
	        	done.push(campaign_inactive.src.indexOf("inactif"));
	        };
	        if (operation_name_filled.src.indexOf("inactif") !== -1){
	            done.push(operation_name_filled.src.indexOf("inactif"));
	        }
	        if (canal_chosen_inactive.src.indexOf("inactif") !== -1 && $(".canal-option .option-valid").length > 0 ){
	            done.push(canal_chosen_inactive.src.indexOf("inactif"));
	        }
	        if (done.length > 0) {
	        	/*document.getElementById('name-op').disabled = false;*/
	        	$('.foot-btn-bg').addClass('hidden');
	        	$('#name_operation').removeClass('hidden');

	        }
	        else {
	        	/*document.getElementById('name-op').disabled = true;*/
	        	/*document.getElementById('name-op').value = "";*/
	        	$('.foot-btn-bg').removeClass('hidden');
	        	$('#name_operation').addClass('hidden');
	        };
    	};
    };

 	var campaign = document.getElementById("campaign");
 	var campaign_list;var action_list;
 	if (campaign){
        campaign_list = campaign.getElementsByClassName("-liste");
	    action_list = campaign.getElementsByClassName("list-group-item");
 	}
	var campaign_inactive = document.getElementById("inactive-campaign");
	var searched_profile_inactive = document.getElementById("searched-profile-inactive");
	var operation_name_filled = document.getElementById("operation-name-filled");
	var population_scored_inactive = document.getElementById("population-scored-inactive");
	var canal_chosen_inactive = document.getElementById("diffusion-canal-filled");

    if (action_list){
        for (var j = 0; j < action_list.length; j++) {
            action_list[j].addEventListener("click", function() {
            var current = document.getElementsByClassName("active");
            current[0].className = current[0].className.replace(" active", "");
            this.className += " active";
          });
        };
    }

    setIcon = function(img, input, file) {

        if (($(input).val() !== '' && $(file).val() !== '') && ($(input).val() !== null && $(file).val() !== null )) {
        	img.setAttribute("src", "/maas_website/static/src/img/ico-coche-actif.png");
        }
        else {
        	img.setAttribute("src", "/maas_website/static/src/img/ico-coche-inactif.png");
        };
        getActive();
    };

	if (searched_profile_inactive !== null || population_scored_inactive !== null) {
	    setIcon(searched_profile_inactive, "#input-profile-search", "#file-profile-search");
	    setIcon(population_scored_inactive, "#input-population-scored", "#file-population-scored");
	}

    /*$("#name-op")
    .on('keyup', function() {
    	if ($("#name-op").val() !== '') {
    		$('.foot-btn-bg').removeClass('hidden');
    	}
    	else {
			$('.foot-btn-bg').addClass('hidden');
    	};
    });*/

    $("#file-profile-search")
    .on('change', function() {
    	setIcon(searched_profile_inactive, "#input-profile-search", "#file-profile-search");
    });

    $("#file-population-scored")
    .on('change', function() {
    	setIcon(population_scored_inactive, "#input-population-scored", "#file-population-scored");
    });

    $('#input-profile-search')
    .on('change', function(e) {
        var files = $(this)[0].files;
        document.getElementById('input_value').value = files[0].name;
        setIcon(searched_profile_inactive, "#input-profile-search", "#file-profile-search");
    });

    $('#input-population-scored')
    .on('change', function(e) {
        var files = $(this)[0].files;
        document.getElementById('input_value2').value = files[0].name;
        setIcon(population_scored_inactive, "#input-population-scored", "#file-population-scored");
    });

    $("#canal-selection").on('change', function(e){
        setIcon(canal_chosen_inactive, "#canal-selection", "#canal-selection");
    });
    if(canal_chosen_inactive){
        $(".canal-option[selected='1']").each(function(){
            $("#canal-selection").val($(this).val());

        });
        setIcon(canal_chosen_inactive, "#canal-selection", "#canal-selection"); /* default canal check */


    }


    $(".foot-btn")
    .on('click', function() {
    	$(".operation-modal-email").text($('#').val());
    	var current = document.getElementsByClassName("active");
    	if (current[0].hasAttribute("campaign-id")) {
	    	document.getElementById("campaign_id").value = parseInt(current[0].attributes['campaign-id'].value);
	    	document.getElementById("action_id").value = parseInt(current[0].attributes['id'].value);
    	}
    	else {
    		document.getElementById("campaign_id").value = current[0].attributes['id'].value
    	};

  		var form = new FormData();
  		form.append("name", $('#operation-name-input').val());
  		form.append("campaign_id", $('#campaign_id').val());
  		form.append("action_id", $('#action_id').val());
  		form.append("searched_profile_desc", $('#file-profile-search').val());
  		form.append("population_scored_desc", $('#file-population-scored').val());
  		form.append("population_scored_datafile", $('#input-population-scored')[0].files[0]);
  		form.append("searched_profile_datafile", $('#input-profile-search')[0].files[0]);
  		form.append("canal", $("#canal-selection").val());

		var xhr = new XMLHttpRequest();
		$('#loadingGIF').css({'position':'fixed','margin':'0px', 'padding': '0px', 'position': 'fixed', 'right': '0px', 'top': '0px', 'width': '100%', 'height': '100%','background-position':'center'})
		$('#loadingGIF').show();
		$('.overlaying').css({ opacity: 0.7, 'width':$(document).width(),'height':$(document).height()});
  		xhr.onreadystatechange = function() {
  		 	if (xhr.readyState === 4 && xhr.status === 200) {
  		 	setTimeout(function() {
             	$('#loadingGIF').hide();
              	$('.overlaying').css({ 'opacity': 1});
  		    	$('#popup-information').modal({
                    backdrop: 'static',
                });
  		 		}, 1000);
  		    };
  		};
		xhr.open("post", "/operation/launch/", true);
      	xhr.timeout = 600000; // time in milliseconds

		xhr.ontimeout = function (e) {
			$('#loadingGIF').hide();
			$('.overlaying').css({ 'opacity': 1});
			$('#popup-information').modal('show');
		};
		xhr.send(form);
      });


    /*------------- create campaign -------------*/

    $(".create-campaign").on('click', function() {
    	var test_input=0;
    	$(".-liste").each(function(e){
    	 current=$(this);
    	 if(current.find('input')[0]){
    	 	test_input++;
    		}
    	});
    	if(!($("#collapse-campaign").is(":visible")))
    	    $("#all-campaigns").click();
    	if(test_input==0){
    		var newNode = document.createElement("a");
    		newNode.className = "-liste";
    		newNode.setAttribute("data-toggle", "collapse");

    		$("#collapse-campaign").append(newNode);
    		var newInput = document.createElement("input");
	    	newInput.className = "-liste-input";
	    	newInput.type = "text";
	    	if ($('.list-campagne').length > 0) {
	    		var width = parseInt($('.list-campagne')[0].clientWidth) - 100;
	    	}
	    	else if ($('.list-campagne-bis').length > 0) {
	    		var width = parseInt($('.list-campagne-bis')[0].clientWidth) - 80;
	    	};
            newInput.setAttribute("required", "required");
	    	newInput.setAttribute("style", 'width:'+width+'px; border: 1px solid #87CEEB;');
	    	newInput.setAttribute("placeholder", "Taper un texte...");
	    	newNode.appendChild(newInput);
            newInput.focus();
            $(".-liste-input").on("focusout",function(event){
                var $target = $(event.target);
                $target.closest("a").remove();
            });
			var node = document.getElementsByClassName("-liste-input")[0];
			node.addEventListener("keyup", function(e) {
		        if (e.key === "Enter") {
			        $.ajax({
			            dataType: 'json',
			            url: '/campaign/create/' + $(".-liste-input").val(),
			            type: 'POST',
			            proccessData: false,
			            data: {},
			            }).then(function(records) {
			                var data = records.reduce(function(a, b) {
			                    a.push({name: b['name'], id: b['id'], });
			                    return a;
			                }, []);
			                newInput.remove();
			                var newSpan = document.createElement("span");
			                newSpan.innerText = data[0]['name'];
			                newNode.appendChild(newSpan);
			                //location.reload();
			                $("#campaign").load(location.href + ' #campaign>*', null, function(){
			                    add_liste_click();
			                    add_list_group_item_click();
                                update_badge_info_count($("#filter-operation").val());
			                    $(".-liste[id='"+data[0]['id']+"']").click();
			                });
                            /*for (var j = 0; j < action_list.length; j++) {
                                action_list[j].addEventListener("click", function() {
                                var current = document.getElementsByClassName("active");
                                current[0].className = current[0].className.replace(" active", "");
                                this.className += " active";
                              });
                            };*/
					});
		        };
			});
	    }

    });

    /*-------------- create action -----------------*/
    $(".create-action").on('click', function() {
    	var test_input=0;
    	$('.list-group-item').each(function(e){
    	 current=$(this);
    	 if(current.find('input')[0]){
    	 	test_input++;
    		}
    	});
    	if (test_input === 0){
    	    var active_campaign = $(".-liste").filter(".active");
            var active_action = $(".list-group-item").filter(".active");
            var parent_to;
            var campaign_id;
            if (active_campaign.length > 0 && active_action.length === 0){
                parent_to = active_campaign.parent().find(".panel-collapse[id=collapse"+String(active_campaign[0].attributes.id.value)+"]");
                if(!$("#collapse"+active_campaign[0].attributes.id.value+"").is(":visible"))
                    active_campaign.click();
                campaign_id = parseInt(active_campaign[0].attributes.id.value);

            }
            else if (active_campaign.length === 0 && active_action.length > 0){
                parent_to = active_action.parent();
                campaign_id = parseInt(active_action[0].attributes.campaign.value);
            }
            var newNode = document.createElement("li");
            newNode.className = "list-group-item";
            newNode.setAttribute("campaign-id", campaign_id);
            parent_to.append(newNode);
            var newInput = document.createElement("input");
            newInput.className = "-action-input";
            newInput.type = "text";
            if ($('.list-campagne').length > 0) {
                var width = parseInt($('.list-campagne')[0].clientWidth) - 170;
            }
            else if ($('.list-campagne-bis').length > 0) {
                var width = parseInt($('.list-campagne-bis')[0].clientWidth) - 100;
            };
            newInput.setAttribute("required", "required");
            newInput.setAttribute("style", 'width:'+width+'px;');
            newInput.setAttribute("placeholder", "Taper un texte...");
            newInput.setAttribute("campaign",campaign_id)
            newNode.appendChild(newInput);
            newInput.focus();
            $(".-action-input").on("focusout", function(event){
                var $target = $(event.target);
                $target.closest("li").remove();

            });
            var node = document.getElementsByClassName("-action-input")[0];
            node.addEventListener("keyup", function(e) {
                if (e.key === "Enter") {
                    $.ajax({
                        dataType: 'json',
                        url: '/action/create/' + $(".-action-input").val() + '/' + $(this)[0].attributes.campaign.value,
                        type: 'POST',
                        proccessData: false,
                        data: {},
                        }).then(function(records) {
                            var data = records.reduce(function(a, b) {
                                a.push({name: b['name'], id: b['id'], });
                                return a;
                            }, []);
                            newInput.remove();
                            if((campaign.classList.contains('in'))){
                                campaign.classList.remove('in');
                            }
                            var newA = document.createElement("a");
                            newA.href = '#';
                            newNode.appendChild(newA);
                            newNode.setAttribute("id", parseInt(data[0]['id']));
                            var newSpan = document.createElement("span");
                            newSpan.innerText = data[0]['name'];
                            newSpan.setAttribute("data-oe-model", "sale.campaign.action");
                            newSpan.setAttribute("data-oe-id", data[0]['id']);
                            newSpan.setAttribute("data-oe-field", "name");
                            newSpan.setAttribute("data-oe-type", "char");
                            newSpan.setAttribute("data-oe-expression", "ca.name");
                            newA.appendChild(newSpan);
                            var newSpan = document.createElement("span");
                            newSpan.className = "badge badge badge-action-info";
                            newSpan.innerText = 0;
                            newA.appendChild(document.createTextNode('\u00A0'));
                            newA.appendChild(newSpan);
                            var newImg = document.createElement("img");
                            newImg.className = "ico-delete";
                            newImg.setAttribute("action-id", parseInt(data[0]['id']));
                            newImg.setAttribute("src", "/maas_website/static/src/img/ico-no.png");
                            newImg.addEventListener("click", function() {
                                deleteCampaignAction('action', parseInt($(this)[0].attributes['action-id'].value));
                            });
                            newA.appendChild(document.createTextNode('\u00A0'));
                            newA.appendChild(newImg);
                            $("#campaign").load(location.href + ' #campaign>*', null, function(){
			                    add_liste_click();
			                    add_list_group_item_click();
			                    update_badge_info_count($("#filter-operation").val());
			                    $(".-liste[id='"+campaign_id+"']").click();
			                    $(".list-group-item[id='"+data[0]['id']+"']").click();
			                });
                            /*for (var j = 0; j < campaign_list.length; j++) {
                                campaign_list[j].addEventListener("click", function() {
                                var current = document.getElementsByClassName("active");
                                current[0].className = current[0].className.replace(" active", "");
                                this.className += " active";
                              });
                            };*/
                            //location.reload();
                    });
                };
            });

    	}
    });

    $("#input-profile-search").add("#input-population-scored").change(function () {
        var fileExtension = ['csv'];
        if ($.inArray($(this).val().split('.').pop().toLowerCase(), fileExtension) === -1) {
            var input_value = $("#input_value");
            var input_value2 = $("#input_value2");
            input_value.replaceWith(input_value.val('').clone(true))
            input_value2.replaceWith(input_value2.val('').clone(true))
            $("#error_extension").modal();
            return false;
        }
      }); 

	$('#search').on('change keyup', function() {
	    var searchTerm, ContainerID;
		searchTerm = $(this).val();
		var exp = new RegExp($(this).val(), 'i');
		$(".-liste:not([id='all-campaigns'])").each(function() {
			ContainerID = '#' + $(this).attr('id');
			$.extend($.expr[':'], {
				'contains': function(elem, i, match, array) {
				return (elem.textContent || elem.innerText || '').toLowerCase()
				.indexOf((match[3] || "").toLowerCase()) >= 0;
                }
            });
            $(ContainerID + ':not(:contains(' + searchTerm + '))').hide();
            $(ContainerID + ':contains(' + searchTerm + ')').show();
		});
		$('li[class="list-group-item"]').each(function(e) {
			var $me = $(this);
			var $parent = $me.parent('ul');
			var Id = 'collapse' + String($parent.attr('id').slice(10));
			var campaign = document.getElementById(Id);
			
			if(searchTerm !== ''){
				if(!$me.text().match(exp)){
				    $me.hide();
                } else {
                    $('#' + String($parent.attr('id').slice(10))).show();
                    campaign.classList.add('in');
                    $me.show();
                }
			} else {
				campaign.classList.remove('in');
				$('#-liste').show();
				$('.list-group-item').show();
			}

		});
        if (searchTerm !== ''){
		    $(".-liste[deleted='deleted']").hide();
		}
		else{
		    $(".-liste[deleted='deleted']").show();
		}

		if(!$("#collapse-campaign").is(":visible"))
		    $("#all-campaigns").click();
	});

	$('#search_operation').on('change keyup', function(e) {
	    $('.accordian-body').collapse('hide');
  		e.preventDefault();
		var searchTerm, ContainerID;
		searchTerm = $(this).val();
		var active_menu = $('.-liste.active');
		if (active_menu.length === 0)
		    active_menu = $('.list-group-item.active');
		$('.ligne-operation').each(function() {
			ContainerID = '#' + $(this).attr('id');
			$.extend($.expr[':'], {
				'contains': function(elem, i, match, array) {
				return (elem.textContent || elem.innerText || '').toLowerCase()
				.indexOf((match[3] || "").toLowerCase()) >= 0;
			}
            });
            $(ContainerID + ':not(:contains(' + searchTerm + '))').hide();
            $(ContainerID + ':contains(' + searchTerm + ')').show();

		});
		paginate_all_operation(1);
    });

	var list_done = [];
	add_list_group_item_click()
	function add_list_group_item_click(){
	    $('.list-group-item').on('click', function(e){
            $(".-liste").removeClass("active");
            $(".list-group-item").removeClass("active");
            $(this).addClass("active");
            $('.ligne-operation').removeClass('fade-row');
            $('.title-pager').removeClass('pager-hidden');
            $('.accordian-body').collapse('hide');
            e.preventDefault();
            var value = $(this)[0].attributes.id.value;
            var parent = $(this);
            var campaign_id = $(this)[0].parentElement.attributes.id.value.split('list-group')[1];
            $('.ligne-operation').each(function(){
               if ($(this).context.hasAttribute("campaign-id") && $(this).context.attributes['campaign-id'].value === campaign_id){
                    $(this).show();
               }
            });
            $('.table .operation-body').find('tr').each(function(e) {
                var $me = $(this).children('td:nth-child(1)');
                //if ($me.context.classList.contains("ligne-operation")) {
                    $('.ligne-operation').each(function() {
                        $.extend($.expr[':'], {
                            'contains': function(elem, i, match, array) {
                            return (elem.textContent || elem.innerText || '').toLowerCase()
                            .indexOf((match[3] || "").toLowerCase()) >= 0;
                        }
                        });
                        if ($(this).context.hasAttribute('action-id')){

                                var ContainerID =  '#'+($(this).context.attributes.id.value).replace('collapse-infos','');
                                var text= $(this).context.attributes["action-id"].value;
                                if (text === value){
                                    $(ContainerID).show();
                                    $(ContainerID).addClass('topaginated');
                                }
                                else{
                                    $(ContainerID).hide();
                                    $(ContainerID).removeClass('topaginated');
                                }

                        }
                        /*else if (!$(this).context.hasAttribute('action-id')){
                            var ContainerID =  '#'+($(this).context.attributes.id.value).replace('collapse-infos','');
                            $(ContainerID).hide();
                            $(ContainerID).removeClass('topaginated');

                        }*/

                });

            });
            paginate_all_operation(1);

            if($('#operaction_creation .-liste').filter("active")){
                $("#inactive-campaign").attr("src", "/maas_website/static/src/img/ico-coche-actif.png");
            }

        });

        $(".list-group-item").on('dblclick',function(event){
            var $target = $(event.target);
            $target.closest("li").addClass("hidden");
            $target.closest("li").next().removeClass("hidden");
            $target.closest("li").next().find("input").focus();

            $(".action-text-change").on("keyup", function(e) {
            if (e.key === "Enter") {
                    actionName = $(this).val();
                    $.ajax({
                        dataType: 'json',
                        url: '/action/update/' + actionName +'/'+ parseInt($(this)[0].attributes.id.value.replace("action","")),
                        type: 'POST',
                        proccessData: false,
                        data: {},
                        }).then(function(records) {
                            var data = records.reduce(function(a, b) {
                                a.push({name: b['name'], id: b['id'], });
                                return a;
                            }, []);
                             $("#campaign").load(location.href + ' #campaign>*', null, function(){
			                    add_liste_click();
			                    add_list_group_item_click();
                                update_badge_info_count($("#filter-operation").val());
			                    var parent = $(".list-group-item[id='"+data[0]['id']+"']")[0].attributes.campaign.value;
			                    $(".-liste[id='"+parent+"']").click();
			                    $(".list-group-item[id='"+data[0]['id']+"']").click();
			                });
                        });
                    };
                });
        });

        // Rename Action
        $(".action-text-change").on("focusout", function(event){
            var $target = $(event.target);
            $target.closest("div").addClass("hidden");
            $(".list-group-item[id="+$target[0].attributes.id.value.replace("action","")+"]").removeClass("hidden");
        });

        //Delete action button
        $('.ico-delete').on('click', function() {
            if ($(this)[0].hasAttribute('campaign-id')) {
                deleteCampaignAction('campaign', $(this)[0].attributes['campaign-id'].value);
            } else if ($(this)[0].hasAttribute('action-id')) {
                deleteCampaignAction('action', $(this)[0].attributes['action-id'].value);
            };
        });

        getActive();
	}


    function add_liste_click(){
        $(".-liste").on('click', function(e){
            $(".list-group-item").removeClass("active");
            $(".-liste").removeClass("active");
            $(this).addClass("active");
            $('.ligne-operation').removeClass('fade-row');
            $('.title-pager').removeClass('pager-hidden');
            $('.accordian-body').collapse('hide');
            e.preventDefault();
            currentHeight = $('.panel-group')[0].offsetHeight;
            if (currentHeight >= 440) {
                $('.campagne').css({'height': currentHeight + 'px', 'overflow': 'scroll', 'overflow-x': 'hidden', 'overflow-y': 'auto'});
            }
            else {
                $('.campagne').css({'overflow-x': 'hidden', 'overflow-y': 'hidden'});
            };
            var value = $(this)[0].attributes.id.value;
            $(".ligne-operation").hide();

            $('.table .operation-body').find('tr').each(function(e) {
                var $me = $(this).children('td:nth-child(1)');
                if ($me.context.classList.contains("ligne-operation")) {
                    $('.ligne-operation').each(function() {
                        $.extend($.expr[':'], {
                            'contains': function(elem, i, match, array) {
                                return (elem.textContent || elem.innerText || '').toLowerCase()
                                .indexOf((match[3] || "").toLowerCase()) >= 0;
                                }
                            });
                        });

                    if ($(this).context.hasAttribute('campaign-id')){
                        var ContainerID =  '#'+($(this).context.attributes.id.value).replace('collapse-infos','');
                        var text= $(this).context.attributes["campaign-id"].value;
                        if (text === value){
                            $(ContainerID).addClass('topaginated');
                            $(ContainerID).show();
                        }

                        else if (value === "all-campaigns"){
                            $(ContainerID).filter("[deleted='deleted']").hide();

                        }
                        else if (value === "deleted-campaigns"){
                           $(ContainerID).filter("[deleted='deleted']").show();

                        }
                        else{
                            $(ContainerID).hide();
                            $(ContainerID).removeClass('topaginated');
                        }
                    }
                }
            });
            paginate_all_operation();

            if($('#operaction_creation .-liste').filter("active")){
                $("#inactive-campaign").attr("src", "/maas_website/static/src/img/ico-coche-actif.png");
                getActive();
            }

	    });

	    $(".-liste:not([folder='parent-folder'])").on('dblclick',function(event){
            var $target = $(event.target);
            $target.closest("a").addClass("hidden");
            $target.closest("a").next().removeClass("hidden");
            $target.closest("a").next().find("input").focus();
            $(".campaign-text-change").on("keyup", function(e) {
            if (e.key === "Enter") {
                campaignName = $(this).val();
                $.ajax({
                    dataType: 'json',
                    url: '/campaign/update/' + campaignName + '/' + parseInt($(this)[0].attributes.id.value.replace("campaign","")),
                    type: 'POST',
                    proccessData: false,
                    data: {},
                    }).then(function(records) {
                        var data = records.reduce(function(a, b) {
                            a.push({name: b['name'], id: b['id'], });
                            return a;
                        }, []);
                         $("#campaign").load(location.href + ' #campaign>*', null, function(){
			                    add_liste_click();
			                    add_list_group_item_click();
			                    update_badge_info_count($("#filter-operation").val());
			                    $(".-liste[id='"+data[0]['id']+"']").click();
			                });
                    });
                };
            });
        });

        // Rename Campaign
        $(".campaign-text-change").on("focusout", function(event){
            var $target = $(event.target);
            $target.closest("div").addClass("hidden");
            $(".-liste[id="+$target[0].attributes.id.value.replace("campaign","")+"]").removeClass("hidden");
        });

        //Delete Campagne button
        $('.ico-delete').on('click', function() {
            if ($(this)[0].hasAttribute('campaign-id')) {
                deleteCampaignAction('campaign', $(this)[0].attributes['campaign-id'].value);
            } else if ($(this)[0].hasAttribute('action-id')) {
                deleteCampaignAction('action', $(this)[0].attributes['action-id'].value);
            };
        });

        getActive();
    }

    add_liste_click();

	function update_pagination_text(){
		$('.page-item.first > a').text('Première');
		$('.page-item.prev > a').text('Précédente');
		$('.page-item.next > a').text('Suivante');
		$('.page-item.last > a').text('Dernière');
	}
	update_pagination_text();

    function getCampagneActive(){
        var campagnes = document.querySelectorAll('.-liste.active');
        return campagnes

    }
    function getActionActive(){
        var actions = document.querySelectorAll('.list-group-item.active');
        return actions
    }
    paginate_all_operation = function(page){
        var operations = filter_operations();
        $('.all-operation-table').each(function () {
            var numPerPage = $('.op_row_input').val();
            var active_campagnes = getCampagneActive();
            var active_actions = getActionActive();
            var ligne_operation;
            var numRows;

            /*archive_function();*/
            deleted_function();

            if($('#search_operation').val() !== ""){
                var searchTerm = $('#search_operation').val();
                $(".ligne-operation:visible").each(function(line){
                    $.extend($.expr[':'], {
                        'contains': function(elem, i, match, array) {
                        return (elem.textContent || elem.innerText || '').toLowerCase()
                        .indexOf((match[3] || "").toLowerCase()) >= 0;
                        }
                    });
                    $('#'+this.attributes.id.value+':not(:contains(' + searchTerm + '))').hide();
                });
            }

            if(active_campagnes.length !== 0 && !active_campagnes[0].hasAttribute("folder") && !active_campagnes[0].attributes.id.value == 'deleted-campaigns'){
                ligne_operation = $(".ligne-operation[campaign-id="+active_campagnes[0].attributes.id.value+"]:visible");
                numRows = ligne_operation.length;
            }
            else if (active_campagnes.length !== 0 && active_campagnes[0].attributes.id.value === 'deleted-campaigns'){
                ligne_operation= $(".ligne-operation[deleted='deleted']:visible");
                numRows = ligne_operation.length;
            }
            else if(active_campagnes.length !== 0 && active_campagnes[0].hasAttribute("folder")){
                ligne_operation= $(".ligne-operation:visible");
                numRows = ligne_operation.length;
            }
            else if (active_campagnes.length === 0 && active_actions.length !== 0){
                ligne_operation = $(".ligne-operation[action-id="+active_actions[0].attributes.id.value+"]:visible");
                numRows = ligne_operation.length;
            }
            else{
                ligne_operation = $(".ligne-operation:visible");
                numRows = ligne_operation.length;
            }

            var first_page = 0;

            $(".ligne-operation:visible").hide();
            ligne_operation.hide().slice(first_page * numPerPage, (first_page + 1) * numPerPage).show();
            if (numRows <= numPerPage) {
                $(".table_pager").hide();
            }
            if(page === null)
                page = 1;
            if (numRows > numPerPage) {
                $('#pagination_pager').replaceWith($('<ul id="pagination_pager" class="pagination-sm"></ul>'));
                $('#pagination_pager').twbsPagination({
                    totalPages: Math.ceil(numRows / numPerPage),
                    visiblePages: 6,
                    startPage: page,
                    onPageClick: function (event, page) {
                        var current_page = page - 1;
                        $(".ligne-operation").hide();
                        ligne_operation.hide().slice(current_page * numPerPage, (current_page + 1) * numPerPage).show();
                        paginate_all_operation_child();
                        $(".table_pager").show();
                    }
                });
            } else if (numRows < numPerPage) {
                $(".table_pager").hide();
            }
            paginate_all_operation_child();
        });
        return operations
    };

    paginate_all_operation_child = function(){
        $(".ligne-operation:not(:visible)").next().hide();
        $(".ligne-operation:visible").next().show();
        update_pagination_text();
    }

    $('.op_row_input').on('change', function (e) {
        $('.ligne-operation').show();
        paginate_all_operation();
	});

    // call paginate_all_operation() to paginate all operation on first view
    paginate_all_operation();

	$('.accordian-body').on('show.bs.collapse', function () {
	    $(this).closest("tbody")
	        .find(".collapse.in")
	        .not(this)
	        .collapse('toggle')
	});

    var created_operation=document.getElementById("operation-name-input")
    if (created_operation){
        created_operation.addEventListener('keyup', function(e){
        if(e.key === "Enter"){
            var img = document.getElementById("operation-name-filled");
            if (evaluation_input($(this)[0].value)){
                img.setAttribute("src", "/maas_website/static/src/img/ico-coche-actif.png");
                $(this).blur();
            }
            else{
                img.setAttribute("src", "/maas_website/static/src/img/ico-coche-inactif.png");
                $(this).blur();
            }

        }
        getActive();

    });
    created_operation.addEventListener("blur",function(){
        var img = document.getElementById("operation-name-filled");
            if (evaluation_input($(this)[0].value)){
                img.setAttribute("src", "/maas_website/static/src/img/ico-coche-actif.png");
            }
            else{
                img.setAttribute("src", "/maas_website/static/src/img/ico-coche-inactif.png");
            }

            getActive();
    });
    }

    var evaluation_input = function(text){
        if(text.length > 0 ){
            return text;
        }
        else{
            return false;
        }
    }

    var input_value = document.getElementById("input_value");
    var input_value2 = document.getElementById("input_value2");
    if (input_value){
        input_value.addEventListener("mouseover",function(){
            $(this).focus();
        });
    }
    if (input_value2){
        input_value2.addEventListener("mouseover",function(){
            $(this).focus();
        });
    }
    $(window).keydown(function(event){
        if ($("#popup-information").is(":visible")) {
            if(event.keyCode === 13) {
                $("#btn-info-ok").click();
                event.preventDefault();
                return false;
            }
        }
    });

    /* ------------------ reload the operation list automatically -------------------------*/
    var idleState = false;
    var idleTimer = null;
    $('*').bind('mousemove click mouseup mousedown keydown keypress keyup submit change mouseenter scroll resize dblclick', function () {
        clearInterval(idleTimer);

        idleState = false;
        idleTimer = setInterval(function () {
            reloadOperationList();
            idleState = true; }, 20000);
    });
    $("body").trigger("mousemove");
    function reloadOperationList(){
        lignes = document.getElementsByClassName('ligne-operation');
        op_list = '';
        if(lignes.length>0)
            op_list = lignes[0].id;
        for(var i = 1; i<lignes.length; i++)
            op_list += '/' + lignes[i].id;
        pagination_active = $('#pagination_pager .active');
        var page = 1;
        if (pagination_active.length !== 0){
            page = parseInt($('#pagination_pager .active')[0].firstChild.innerText);

        }
        var slide_this = $(".slide-this:visible");
        $('#sale-operation').load(location.href + ' #sale-operation>*', null, function(){
            if (opContainer !== null) {
                var operations = opContainer.getElementsByClassName("ligne-operation");
                mouseOverOps(operations);
            }
            if(slide_this.length > 0){
                $("td[colspan=9]").find("div").filter("#collapse-child").removeClass("slide-this");
                $("td[colspan=9]").find("div").filter("#collapse-child").hide();
                $("td[colspan=9]").find("div").filter("#collapse-child[parent='"+slide_this[0].attributes.parent.value+"'][id='"+slide_this[0].attributes.id.value+"']").addClass("slide-this");
                $("td[colspan=9]").find("div").filter("#collapse-child[parent='"+slide_this[0].attributes.parent.value+"'][id='"+slide_this[0].attributes.id.value+"']").show();


                //$("#collapse-child").filter(":not([parent='"+slide_this[0].attributes.parent.value+"'][id='"+slide_this[0].attributes.id.value+"'])").slideUp();
            }
            else{
                $("td[colspan=9]").find("div").filter("#collapse-child").slideUp();
            }
            paginate_all_operation(page);
            addEventIco();
        });
    }

    /* ------------------ add operation child collapsing -------------------------*/
    $(".all-operation-table").click(function(event) {
        event.stopPropagation();
        var $target = $(event.target);
        /*if ( $target.closest("td").attr("colspan") > 1 ) {
            $target.slideUp();
        } else {*/
        var slide_parent = $target.closest("tr").next();
        var slide_element =  $target.closest("tr").next().find("div").filter("#collapse-child");
        $("td[colspan=9]").find("div").filter("#collapse-child").removeClass("slide-this");
        if (slide_element.length > 0)
            slide_element.addClass("slide-this");
        slide_element.slideToggle(function(){
               $("tr.ligne-operation-child").find("div").filter("#collapse-child:not([parent='"+slide_element[0].attributes.parent.value+"'])").slideUp();
            });


    });

    /*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ add first operation child initial ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
    function addEventIco(){
        $(".ico-yes-child").dblclick(function(e){
            e.preventDefault();
        });
        $(".ico-yes-child").click(function(e){
            var $target = $(e.target);
            if (parseInt($("input.edit-value-child[parent='"+$target[0].attributes.parent.value+"']").val()) > 0){
                $target.hide();
                $target.next().removeClass("hidden");
            }
            function get_type(value){
                if (value === 'initial_command')
                    return 'initial_command'
                else if(value === 'other'){
                    return $(".op_sens[parent='"+$target[0].attributes.parent.value+"']")[0].value;
                }
            }
            function get_sens(){
                if ($(".sens[parent='"+$target[0].attributes.parent.value+"']").length > 0)
                    return $(".sens[parent='"+$target[0].attributes.parent.value+"']")[0].value;
                return false
            }
            $.ajax({
                    dataType: 'json',
                    url: '/operation/update/' + parseInt(($target[0].attributes.parent.value).replace('operation','')) + '/' + get_type($target[0].attributes.command.value) + '/' +
                           parseInt($("input.edit-value-child[parent='"+$target[0].attributes.parent.value+"']").val()),
                    type: 'POST',
                    proccessData: false,
                    data: { sens: get_sens()},
                    }).then(function(records) {
                        var data = records.reduce(function(a, b) {
                            a.push({id: b['id'],
                                show_popup: b['show_popup'],
                                available_identifiers: b['available_identifiers'],
                                volume_filled: b['volume_filled'],
                                difference: b['difference'],
                                product_name: b['product_name'],
                                except: b['except'],
                                text: b['text'],
                                maintenance : b['maintenance_mode']
                            });
                            return a;
                        }, []);
                        if (data[0].maintenance === true){
                            location.reload();
                        }
                        if (data[0].show_popup === true && data[0].except === false ) {
                            $('#oe_generic_popup_modal').modal('show');
                            $('.o_available_identifiers').text(data[0].available_identifiers);
                            $('.o_volume_filled').text(data[0].volume_filled);
                            $('.o_difference').text(data[0].difference);
                            $('.o_product_name').text(data[0].product_name);
                            $('.modeling-operation')[0].value = parseInt(data[0].id);
                            $('.available_identifiers')[0].value = parseInt(data[0].available_identifiers);
                            $('.volume_filled')[0].value = parseInt(data[0].volume_filled);
                            if(data[0].available_identifiers === 0){
                                $("#use_available_identifiers").prop( "disabled", true );
                                $("#use_available_identifiers").attr("checked",false);
                                $("#error-message").show();
                            }
                            $("#oe_generic_popup_modal").on('hidden.bs.modal', function () {
                                reloadOperationList();
                            });
                        }
                        else if(data[0].show_popup === true && data[0].except === true){
                            $('#oe_generic_pop_up_except').modal('show');
                            $('#except-text').text(data[0].text);
                        }
                        else {
                            $('#sale-operation').load(location.href + ' #sale-operation>*', null, function(){
                                pagination_active = $('#pagination_pager .active');
                                var page = 1;
                                if (pagination_active.length !== 0){
                                    page = parseInt($('#pagination_pager .active')[0].firstChild.innerText);

                                }
                                paginate_all_operation(page);
                                $("td[colspan=9]").find("div").filter("#collapse-child").hide();
                                $("td[colspan=9]").find("div").filter("#collapse-child[parent='"+$target[0].attributes.parent.value+"']").slideToggle(function(){

                                    addEventIco();
                                });
                                $('#head-value').load(location.href + ' #head-value>*', null, null);

                             });

                        };
                });
        });

        $(".ico-no-child").click(function(e){
            var $target = $(e.target);
            $("#qty-extracted-"+$target[0].attributes.parent.value.replace("operation","")+"").val("");
        });
        $(".ico-no").click(function(e){
            var $target = $(e.target);
            $('#oe_generic_popup_cancel').modal('show');
            $('#oe_generic_popup_cancel').find(".operation-name").text($target[0].attributes.name.value);
            $('#oe_generic_popup_cancel').find(".operation-deleted-parent")[0].value = $target[0].attributes.parent.value;
            $('#oe_generic_popup_cancel').find(".cancel-operation")[0].value = parseInt(($target[0].attributes.id.value).replace('operation',''));

        });
        $(".ico-yes").click(function (e){
            var $target = $(e.target);
            $target.next().removeClass("hidden");
            $target.hide();
            $.ajax({
                    dataType: 'json',
                    url: '/operation/validate/' + parseInt($target[0].attributes.id.value),
                    type: 'POST',
                    proccessData: false,
                    data: {},
                    }).then(function(records) {
                        var data = records.reduce(function(a, b) {
                            a.push({id: b['id'],
                                show_popup: b['show_popup'],
                                available_identifiers: b['available_identifiers'],
                                volume_filled: b['volume_filled'],
                                difference: b['difference'],
                                product_name: b['product_name'],
                                except: b['except'],
                                text: b['text']
                            });
                            return a;
                        }, []);
                        if (data[0].show_popup === true && data[0].except === false ) {
                            $('#oe_generic_popup_modal').modal('show');
                            $('.o_available_identifiers').text(data[0].available_identifiers);
                            $('.o_volume_filled').text(data[0].volume_filled);
                            $('.o_difference').text(data[0].difference);
                            $('.o_product_name').text(data[0].product_name);
                            $('.modeling-operation')[0].value = parseInt(data[0].id);
                            $('.available_identifiers')[0].value = parseInt(data[0].available_identifiers);
                            $('.volume_filled')[0].value = parseInt(data[0].volume_filled);
                            if(data[0].available_identifiers === 0){
                                $("#use_available_identifiers").prop( "disabled", true );
                                $("#use_available_identifiers").attr("checked",false);
                                $("#error-message").show();
                            }
                            $("#oe_generic_popup_modal").on('hidden.bs.modal', function () {
                                reloadOperationList();
                            });

                        }
                        else if(data[0].show_popup === true && data[0].except === true){
                            $('#oe_generic_pop_up_except').modal('show');
                            $('#except-text').text(data[0].text);
                        }
                        else {
                            $('#sale-operation').load(location.href + ' #sale-operation>*', null, function(){
                                pagination_active = $('#pagination_pager .active');
                                var page = 1;
                                if (pagination_active.length !== 0){
                                    page = parseInt($('#pagination_pager .active')[0].firstChild.innerText);

                                }
                                paginate_all_operation(page);
                                $("td[colspan=9]").find("div").filter("#collapse-child").hide();
                                $("td[colspan=9]").find("div").filter("#collapse-child[parent='"+$target[0].attributes.parent.value+"']").show(function(){
                                    addEventIco();
                                });
                             });
                        };
                });

        });
        $(".ico-delete-operation2").click(function (e){
            var $target = $(e.target);
            $('#oe_generic_popup_delete').modal('show');
            $('#oe_generic_popup_delete').find(".operation-name").text($target[0].attributes.name.value);
            $('#oe_generic_popup_delete').find(".operation-deleted-parent")[0].value = $target[0].attributes.parent.value;
            $('#oe_generic_popup_delete').find(".deleted-operation")[0].value = parseInt(($target[0].attributes.id.value).replace('operation',''));
        });


        $(".ico-info-child").click(function() {
				$.ajax({
		            dataType: 'json',
		            url: '/operation/message/list/child/' + parseInt((this.attributes.id.value).replace('child','')),
		            type: 'POST',
		            proccessData: false,
		            data: {},
		            }).then(function(res) {
						var op_messages = document.getElementById('op_messages');
						var modal_dialog = $('#operation_info_modal');
						var modal_restricted_access = $('#operation_restricted_access_modal');
						op_messages.innerHTML = "";
						if (res[0] !== undefined && res[0] !== null) {
							if (res[0].length > 0) {

								for (var i = 0; i < res[0].length; i++) {
									var line_doc = document.createElement('tr');
		                            line_doc.setAttribute("class" , "test");
									var doc_author = document.createElement('td');
									var doc_body = document.createElement('td');
									var doc_date = document.createElement('td');
									doc_author.innerHTML =  res[0][i]['author'];
									doc_body.innerHTML =  res[0][i]['body'];
									doc_date.innerHTML =  res[0][i]['date'];
									line_doc.appendChild(doc_author);
									line_doc.appendChild(doc_body);
									line_doc.appendChild(doc_date);
									op_messages.appendChild(line_doc);
								};
		                        modal_dialog.modal('show');
							};
						};
				});
            });


    }
    addEventIco();
    filter_change_action();
    function filter_change_action(){
        $("#filter-operation").change(function() {
           $(this).find(":selected").each(function () {
                   paginate_all_operation(1);
                   update_badge_info_count($(this).val());
           });
         });
    }

    function update_badge_info_count(filter){
        switch(filter){
                case "all-operations":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").length;
                        $(this).text(count);
                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").length;
                        $(this).text(count);
                    });
                    break;
                case "last-30-days":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_30_days = new Date(date.setDate(date.getDate() - 30));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_30_days.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_30_days = new Date(date.setDate(date.getDate() - 30));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_30_days.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });
                    break;
                case "last-3-months":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_3_months = new Date(date.setMonth(date.getMonth() - 3));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_3_months.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_3_months = new Date(date.setMonth(date.getMonth() - 3));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_3_months.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });

                    break;
                case "last-6-months":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_6_months = new Date(date.setMonth(date.getMonth() - 6));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_6_months.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_6_months = new Date(date.setMonth(date.getMonth() - 6));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_6_months.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });
                    break;
                case "last-12-months":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_12_months = new Date(date.setMonth(date.getMonth() - 12));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_12_months.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            var date = new Date();
                            var last_12_months = new Date(date.setMonth(date.getMonth() - 12));
                            var today = new Date();

                            return new Date($(this).attr("date")).getTime() > last_12_months.getTime() &&
                                       new Date($(this).attr("date")).getTime() < today.getTime()
                        }).length;
                        $(this).text(count);


                    });

                    break;
                case "trimester-1":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(){
                            return (new Date($(this).attr("date")).getMonth() >= 0) &&
                                       (new Date($(this).attr("date")).getMonth() <= 2)
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return (new Date($(this).attr("date")).getMonth() >= 0) &&
                                       (new Date($(this).attr("date")).getMonth() <= 2)
                        }).length;
                        $(this).text(count);


                    });
                    break;
                case "trimester-2":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return new Date($(this).attr("date")).getMonth() >= 3 &&
                                       new Date($(this).attr("date")).getMonth() <= 5
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return new Date($(this).attr("date")).getMonth() >= 3 &&
                                       new Date($(this).attr("date")).getMonth() <= 5
                        }).length;
                        $(this).text(count);


                    });
                    break;
                case "trimester-3":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return new Date($(this).attr("date")).getMonth() >= 6 &&
                                       new Date($(this).attr("date")).getMonth() <= 8
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return new Date($(this).attr("date")).getMonth() >= 6 &&
                                       new Date($(this).attr("date")).getMonth() <= 8
                        }).length;
                        $(this).text(count);


                    });
                    break;
                case "trimester-4":
                    $(".badge-campaign-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[campaign-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return new Date($(this).attr("date")).getMonth() >= 9 &&
                                       new Date($(this).attr("date")).getMonth() <= 11
                        }).length;
                        $(this).text(count);


                    });
                    $(".badge-action-info").each(function(){
                        var self = $(this);
                        var count = $(".ligne-operation[action-id="+$(this).attr("id")+"][deleted='not deleted']").filter(function(index){
                            return new Date($(this).attr("date")).getMonth() >= 9 &&
                                       new Date($(this).attr("date")).getMonth() <= 11
                        }).length;
                        $(this).text(count);


                    });
                    break;
            }

    }
    filter_context_menu();

    function filter_context_menu(){
        //var filter_saved = localStorage['default-filter'] || 'no-value';
        $.ajax({
            dataType: 'json',
            url: '/operation/filter/get',
            type: 'POST',
            proccessData: false,
            data: {},
            }).then(function(records) {
                if (records.filter){
                    $("#filter-operation").val(records.filter).trigger("change");
                }
        });
        $("#filter-operation").bind("contextmenu", function (event) {
            event.preventDefault();
            $(".custom-menu").finish().toggle(100).
            css({
                left: event.pageX + "px"
            });
        });
        $(document).bind("mousedown", function (e) {
            if (!$(e.target).parents(".custom-menu").length > 0) {
                $(".custom-menu").hide(100);
            }
        });
        $(".custom-menu li").click(function(){
            switch($(this).attr("data-action")) {
                case "default":
                    $.ajax({
                        dataType: 'json',
                        url: '/operation/filter/set/'+$("#filter-operation").val(),
                        type: 'PUT',
                        proccessData: false,
                        data: {},
                    }).then(function(){
                        $("#campaign").load(location.href + ' #campaign>*', null, function(){
			                    add_liste_click();
			                    add_list_group_item_click();
                                update_badge_info_count($("#filter-operation").val());

			            });
                    });
                    break;

            }
            $(".custom-menu").hide(100);
        });
    }
    function filter_operations(){
        var filter = $("#filter-operation").val();
        var operations = [];
        var active_campaign = $(".-liste").filter(".active");
        var active_action = $(".list-group-item").filter(".active");
        if(active_campaign.length > 0 && active_action.length === 0){
            if(active_campaign[0].attributes.id.value !== "all-campaigns")
                $(".ligne-operation[campaign-id="+active_campaign[0].attributes.id.value+"]").show();
            else if (active_campaign[0].attributes.id.value === "all-campaigns")
                $(".ligne-operation").show();
        }
        else if(active_campaign.length === 0 && active_action.length > 0){
            $(".ligne-operation[action-id="+active_action[0].attributes.id.value+"]").show();
        }
        switch(filter){
            case "all-operations":
                $(".ligne-operation:visible").show();
                $(".ligne-operation:visible").each(function(){
                    operations.push($(this))
                });
                break;
            case "last-30-days":
                var date = new Date();
                var last_30_days = new Date(date.setDate(date.getDate() - 30));
                var today = new Date();
                var count=0;
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if((last_30_days.getTime() < date_operation.getTime()) && (date_operation.getTime() < today.getTime())){
                        $(this).show();
                        operations.push($(this));

                    }

                    else{
                        $(this).hide();
                    }
                });
                break;
            case "last-3-months":
                var date = new Date();
                var last_3_months = new Date(date.setMonth(date.getMonth() - 3));
                var today = new Date();
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if((last_3_months.getTime() < date_operation.getTime()) && (date_operation.getTime() < today.getTime())){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }

                });
                break;
            case "last-6-months":
                var date = new Date();
                var last_6_months = new Date(date.setMonth(date.getMonth() - 6));
                var today = new Date();

                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if((last_6_months.getTime() < date_operation.getTime()) && (date_operation.getTime() < today.getTime())){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }
                });
                break;
            case "last-12-months":
                var date = new Date();
                var last_12_months = new Date(date.setMonth(date.getMonth() - 12));
                var today = new Date();
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if((last_12_months.getTime() < date_operation.getTime()) && (date_operation.getTime() < today.getTime())){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }
                    count++;
                });

                break;
            case "trimester-1":
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if( (date_operation.getMonth()>= 0) && (date_operation.getMonth() <= 2) ){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }
                });
                break;
            case "trimester-2":
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if( (date_operation.getMonth()>= 3) && (date_operation.getMonth() <= 5) ){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }
                });
                break;
            case "trimester-3":
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if( (date_operation.getMonth()>= 6) && (date_operation.getMonth() <= 8) ){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }
                });
                break;
            case "trimester-4":
                $(".ligne-operation:visible").each(function(){
                    var date_operation = new Date($(this)[0].attributes.date.value);
                    if( (date_operation.getMonth()>= 9) && (date_operation.getMonth() <= 11) ){
                        $(this).show();
                        operations.push($(this));
                    }

                    else{
                        $(this).hide();
                    }
                });
                break;
        }
        return operations

    }

    /* ---------------------- DELETED function() --------------------------*/
    function deleted_function(){
        var active_side_menu = $(".-liste.active");
        if (active_side_menu.length === 0)
            active_side_menu = $(".list-group-item.active")
        if (active_side_menu.length > 0 && active_side_menu[0].hasAttribute("deleted")){
            if (active_side_menu[0].attributes.deleted.value === "deleted"){
                $(".ligne-operation[deleted='deleted']:visible").show();
                $(".ligne-operation[child_deleted='child_deleted']:visible").show();
                $(".ligne-operation[deleted='not deleted']:visible").filter("[child_deleted='no_child_deleted']").hide();
                child_deleted_function('deleted');

            }
            else if (active_side_menu[0].attributes.deleted.value === "not deleted"){
                $(".ligne-operation[deleted='deleted']:visible").hide();
                $(".ligne-operation[deleted='not deleted']:visible").show();
                child_deleted_function('not deleted');

            }
        }
    }

    function child_deleted_function(arg){
        $(".ligne-operation:visible").each(function(){
            var $target = $(this);
            if(arg === 'deleted'){
                $target.next().find(".child-element[deleted='deleted']").show();
                $target.next().find(".child-element[deleted='not deleted']").hide();
                $target.next().find(".child-element-add").hide();
            }
            else if (arg === 'not deleted'){
                $target.next().find(".child-element[deleted='deleted']").hide();
                $target.next().find(".child-element[deleted='not deleted']").show();
                $target.next().find(".child-element-add").show();
            }

        });
    }

    /* ------------------------------- Indication page ----------------------------------- */
    (async () => {
        var number_indication = parseInt($('#indication_number').val());
        await number_indication;
        if(number_indication > 4){
            $('.lgrid').css({'max-width':'1280px'});
        }
        var $grid = $('.lgrid');
        var number_indication = parseInt($('#indication_number').val());
        var $grid = $('.lgrid').masonry({
                // options
                columnWidth: '.lgrid-sizer',
                itemSelector: '.lgrid-item',
                percentPosition: false,
                initLayout: false,
                //fitWidth: true,
                resize:false,
                gutter:40,
              });
        $grid.masonry( 'on', 'layoutComplete', function() {
            if(number_indication === 1){
                $('.lgrid').css({'left':'200px'});
            }
            if(number_indication === 2){
                 $('.lgrid').css({'left':'100px'});
            }
            if(number_indication === 3){
                $('.lgrid').css({'left':'100px'});
                $('.lgrid-item:last').css({'left':'20%'});
            }
            if(number_indication === 4){
                $('.lgrid').css({'left':'100px'});
            }
            if(number_indication === 5){
                $('.lgrid-item:last').prev("div").css({'left':'50%'});
                $('.lgrid-item:last').css({'left':'15%'});
            }
            if(number_indication === 7){
                $('.lgrid-item:last').css({'left':'33%'});
            }
            if(number_indication === 8){
                $('.lgrid-item:last').prev("div").css({'left':'50%'});
                $('.lgrid-item:last').css({'left':'15%'});
            }
        });
        $grid.masonry('layout');
    })();


    $('.js_change_lang').click(function (ev){
        ev.preventDefault();
        if (document.body.classList.contains('editor_enable')) {
            return;
        }
        var $target = $(ev.currentTarget);
        var redirect = {
            lang: $target.data('url_code'),
            url: encodeURIComponent($target.attr('href').replace(/[&?]edit_translations[^&?]+/, '')),
            hash: encodeURIComponent(window.location.hash)
        };
        window.location.href = "/website/lang/"+redirect.lang+"?r="+redirect.url+redirect.hash;
    });
    $('.ico-menu').on('click',
        function(){
            console.log($('#collapse_menu'));
            console.log($('#home_content'));
            $('#collapse_menu').addClass('col-md-2');
            $('#home_content').removeClass('col-md-12').addClass('col-md-10');
            console.log('---------------');
            console.log($('#collapse_menu'));
            console.log($('#home_content'));
        }
    );

    $('.ico-back-menu').on('click',
        function(){
            console.log($('#collapse_menu'));
            console.log($('#home_content'));
            $('#collapse_menu').removeClass('col-md-2');
            $('#home_content').removeClass('col-md-10').addClass('col-md-12');
            console.log('---------------');
            console.log($('#collapse_menu'));
            console.log($('#home_content'));
        }
    );

});
