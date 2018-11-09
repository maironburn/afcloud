jQuery.fn.reset = function () {
  $(this).each (function() {this.reset();});
}


/**
 *	Operaciones comunes de fecha y hora
 */
var Dates = function(){
	this.days = new Array(_translate("Sunday"),_translate("Monday"),_translate("Tuesday"),_translate("Wenesday"),_translate("Thursday"),
                          _translate("Friday"),_translate("Saturday"));

	Dates.prototype.get_Date = function(){
		var now = new Date();
		var hours=now.getHours().toString();
		var mins= now.getMinutes().toString();

		hours=(hours.length==1 ? '0'+hours :hours);
		mins=(mins.length==1 ? '0'+mins : mins);

		return this.days[now.getDay()]+" "+now.getDate()+", "+hours+":"+mins;
	}
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var AJAXSTUFF={

	/**
	 * Contenido del diccionario content
	 * content.url  : determina el modulo a instanciar
	 * content.data : datos enviados en el request
	 * content.type : tipo de solicitud (GET o POST)
	 * callback; funcion q procesa la respuesta
	 */
	makeRequest: function(content, callback){


		$.ajax({
		    // la URL para la peticion
		    url : content.url,
		    beforeSend: function(xhr, settings) {
		        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", content.csrfmiddlewaretoken);
		        }
		    }
		,
		    cache: false,
		    // la informacion a enviar
		    // (tambien es posible utilizar una cadena de datos)
		    data : content.data,

		    //  POST o GET
		    type : content.type,

		    // el tipo de informacion que se espera de respuesta
		    dataType : 'json',

		    // codigo a ejecutar si la peticion es succesful;
		    // la respuesta es pasada como argumento a la funcion
		    success : function(json) {

		    	console.log('success Request');
		    	callback(json.data);


		    },

		    // si la peticion falla;
		    // son pasados como argumentos a la funcion
		    // el objeto de la peticion en crudo y codigo de estatus de la peticion
		    error : function(xhr, status) {
		    	console.log('error en la peticion ajax');
		    },

		    // codigo a ejecutar sin importar si la peticion falla o no
		    complete : function(xhr, status) {
		    	console.log('Peticion completada');
		    }
		});

	}
	,

	get_csrfmiddlewaretoken: function() {
	     return $('[name="csrfmiddlewaretoken"]').val();
	},

	BuildDictionaryFromObjectRequest: function (data, searchedKeysArray, KeysCollection){

		var dictio={};

		for (i=0; i<KeysCollection.length; i++){

			if( $.inArray(KeysCollection[i], searchedKeysArray )!== -1 ){
				dictio[KeysCollection[i]]=data[KeysCollection[i]];
			}
			else{
				dictio[KeysCollection[i]]="";
			}
		}

		return dictio;
	}
	,
	RequestDefinition : function (data){

		var content ={};
		content['type'] =data.request;
		content['url'] =data.url;
		content['data']= data.data;
        content['csrfmiddlewaretoken']= data.csrftoken
		return content;
	}
	,

	getSpecificRequest: function(data, action, url){

      var datos= {}
      datos.url  = url;
      datos.data = {};
      datos.data ['data']   = data;
      datos.data ['action'] = action;

      return datos;
	}
}




function encode_utf8(s) {
	  return unescape(encodeURIComponent(s));
	}


function decode_utf8(s) {

    var retono='';
    try{
      retono=decodeURIComponent(escape(s));
    }
	  catch(e){
      retono=s;
    }

    return retono;
	}

function encode64(input) {

	var keyStr = "ABCDEFGHIJKLMNOP" +
	"QRSTUVWXYZabcdef" +
	"ghijklmnopqrstuv" +
	"wxyz0123456789+/" +
	"=";

    input = escape(input);
    var output = "";
    var chr1, chr2, chr3 = "";
    var enc1, enc2, enc3, enc4 = "";
    var i = 0;

    do {
       chr1 = input.charCodeAt(i++);
       chr2 = input.charCodeAt(i++);
       chr3 = input.charCodeAt(i++);

       enc1 = chr1 >> 2;
       enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
       enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
       enc4 = chr3 & 63;

       if (isNaN(chr2)) {
          enc3 = enc4 = 64;
       } else if (isNaN(chr3)) {
          enc4 = 64;
       }

       output = output +
          keyStr.charAt(enc1) +
          keyStr.charAt(enc2) +
          keyStr.charAt(enc3) +
          keyStr.charAt(enc4);
       chr1 = chr2 = chr3 = "";
       enc1 = enc2 = enc3 = enc4 = "";
    } while (i < input.length);

    return output;
 }
