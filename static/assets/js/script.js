var keywords=['role','base','input','init','legal','true','next','does','goal','terminal','distinct','not',]
function getCookie(name){var cookieValue=null;if(document.cookie&&document.cookie!=''){var cookies=document.cookie.split(';');for(var i=0;i<cookies.length;i++){var cookie=jQuery.trim(cookies[i]);if(cookie.substring(0,name.length+ 1)==(name+'=')){cookieValue=decodeURIComponent(cookie.substring(name.length+ 1));break;}}}
return cookieValue;}
function ajax(url,data,callback){data['csrfmiddlewaretoken']=getCookie('csrftoken')
$.get(url,data,callback);}