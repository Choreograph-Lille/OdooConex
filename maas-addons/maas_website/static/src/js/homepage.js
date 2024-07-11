$(document).ready(function(){
    function ajustWidth() {
        var leftPix = $(window).width() - 115;
        $("#scrollup").css("left", leftPix + "px");
        if($(window).width() > 770) {
            var thewidth = ($(window).width() - 800)/2;
            $('.left_form').css("width",thewidth + "px");
            $('.left_form').css("height","394px");
            $('.right_form').css("width",thewidth + "px");
            $('.right_form').css("height","394px");
        }else {
            $('.left_form').css("width","0px");
            $('.right_form').css("width","0px");
            $('.left_form').css("height","0px");
            $('.right_form').css("height","0px");
        }
    }
    $('.close').on('click',
        function(){
            var vid = document.getElementById("playerVideo");
            vid.pause();
        }
    );
    $(window).scroll(function() {
        var s = $(window).scrollTop();
        if (s > 250) {
            $('.scrollup').fadeIn();
        } else {
            $('.scrollup').fadeOut();
        }
    });
    $('#playVideo').on('click',
        function(ev) {
            var vid = document.getElementById("playerVideo");
            vid.play();
        }
    );
    $('.redirect').click(
        function(param) {
            param.preventDefault();
            var destination =  $(this).attr("href");
            $("html, body").animate({ scrollTop: $(destination).offset().top }, 500);
        }
    );
    ajustWidth();
    $(window).resize(function () {
        ajustWidth();
    });
    $('.btnOK').click(
        function() {
            $('.thankyou').hide();
            $('.form_elements').show();
            $('.form_elements input:not(:submit)').val('');
        }
    );
    history.pushState(null, null, location.href);
    window.onpopstate = function () {
        history.go(1);
    };

    function accept_ck(){
        var cookies = $('#cookies');
        cookies.hide();
    }
    

})

//odoo.define('maas_website.Homepage',function(require){
//	"use strict";
//
//			$(function(){
//				$('#playVideo').click(
//					function() {
//						var vid = document.getElementById("playerVideo");
//						vid.play();
//						$(this).focusout();
//					}
//				);
//				$('.redirect').click(
//					function(param) {
//						param.preventDefault();
//						var destination =  $(this).attr("href");
//						$("html, body").animate({ scrollTop: $(destination).offset().top }, 500);
//					}
//				);
//				ajustWidth();
//				$(window).resize(function () {
//					ajustWidth();
//				});
//				$('.btnOK').click(
//					function() {
//						$('.thankyou').hide();
//						$('.form_elements').show();
//						$('.form_elements input:not(:submit)').val('');
//					}
//				);
//				/*$("#contactForm").validate(
//					{rules: {
//						civilite: {
//						  required: true
//						}
//					  }}
//				);*/
//				/*$("#contactForm").on('submit', function(e) {
//					var isvalid = $("#contactForm").valid();
//					if (isvalid) {
//						$('#errorMessage').hide();
//						$('#submitButton').hide();
//						e.preventDefault();
//						$.ajax({
//							type: "POST",
//							url: "sendmail.php",
//							data: {myForm:$("#contactForm").serialize()},
//							success: function (data) {
//								if(data ==1) {
//									$('#submitButton').show();
//									$('.form_elements').hide();
//									$('.thankyou').show();
//								}else {
//									alert(data);
//									$('#submitButton').show();
//								}
//							},
//							error: function (data) {
//								alert('data');
//								$('#submitButton').show();
//							},
//						});
//					}else {
//						var errorMsg = "";
//						if($("#civilite-error").length > 0) {
//							errorMsg = "Veuillez sélectionner la civilité";
//						}else if($("#nom-error").length > 0) {
//							errorMsg = "Veuillez saisir le nom";
//						}else if($("#prenom-error").length > 0) {
//							errorMsg = "Veuillez saisir le prénom";
//						}else if($("#societe-error").length > 0) {
//							errorMsg = "Veuillez saisir le nom de la société";
//						}else if($("#email-error").length > 0) {
//							errorMsg = "Veuillez vérifier l'email";
//						}else if($("#phone-error").length > 0) {
//							errorMsg = "Veuillez vérifier le numéro de téléphone";
//						}
//						$("#contactForm label.error").remove();
//						$('#errorMessage').text(errorMsg);
//						$('#errorMessage').show();
//					}
//				});*/
//			});
//			function ajustWidth() {
//				var leftPix = $(window).width() - 115;
//				$("#scrollup").css("left", leftPix + "px");
//				if($(window).width() > 770) {
//					var thewidth = ($(window).width() - 800)/2;
//					$('.left_form').css("width",thewidth + "px");
//					$('.left_form').css("height","394px");
//					$('.right_form').css("width",thewidth + "px");
//					$('.right_form').css("height","394px");
//				}else {
//					$('.left_form').css("width","0px");
//					$('.right_form').css("width","0px");
//					$('.left_form').css("height","0px");
//					$('.right_form').css("height","0px");
//				}
//			}
//			$('.close').click(
//				function(){
//					var vid = document.getElementById("playerVideo");
//					vid.pause();
//				}
//			);
//			$(window).scroll(function() {
//				var s = $(window).scrollTop();
//				if (s > 250) {
//					$('.scrollup').fadeIn();
//				} else {
//					$('.scrollup').fadeOut();
//				}
//			});
//    history.pushState(null, null, location.href);
//    window.onpopstate = function () {
//        history.go(1);
//    };
//
//    function accept_ck(){
//        var cookies = $('#cookies');
//        cookies.hide();
//    }
//
//});

