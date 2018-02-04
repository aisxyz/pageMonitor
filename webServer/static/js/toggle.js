$(document).ready(function(){
	var controlFlag = true;
	$("#siteArea button").click(function(){
		if(controlFlag)
			$('.launchTower').css('display', 'none');
		$(".site").slideToggle("slow", function(){
			if(! controlFlag)
				$('.launchTower').css('display', 'block');
			controlFlag = ! controlFlag;
		});
	});
});

$(document).ready(function(){
	$("#browser").treeview({
		toggle: function(){
			;
		}
	});
});

function choose(elem){
	var ulElem = elem.parentNode.nextSibling.nextSibling;
	var checkboxs = ulElem.getElementsByTagName("input");
	if(elem.checked==true)
		for(var i=0;i<checkboxs.length;i++)
			checkboxs[i].checked=true;
	else
		for(var i=0;i<checkboxs.length;i++)
			checkboxs[i].checked=false;
}