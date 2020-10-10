function winsize(){
	if (!toggled && $(window).width()/$(window).height()>(90/31) ||
		toggled && $(window).width()/($(window).height()-219)>(18/7)){
		$('body').css('justify-content','flex-start');
	} else {
		$('body').css('justify-content','center');
	}
};
window.onload=function(){
	setTimeout(()=>{$('main').slideDown(500)},100);
	winsize();
};
$(window).on('resize',function(){
	winsize();
});

var toggled=false;
$('h2').click(function(){
	var time=300;
	if (toggled) {
		$('form').slideUp(time);
		$('main').css('min-height','9vw');
		setTimeout(()=>{$('h2').css('border-bottom','0')},time);
		toggled=false;
		winsize();
	} else {
		$('main').css('min-height','calc(9vw + 260px)');
		$('form').slideDown(time);
		$('form').css('display','flex');
		$('h2').css('border-bottom','1px solid black');
		toggled=true;
		setTimeout(()=>{winsize()},time);
	}
});

$('form').on('submit',function submit(e){
	e.preventDefault();
	$('.wrap').css('display','flex');
	$('.process').css('display','block');
	var form=new FormData();
	form.append('mode',$('#mode').val());
	$.each($('#file')[0].files, function(i, file) {
		form.append('file', file);
	});
	$.ajax({
		url:         'huffpress.php',
		type:        'POST',
		processData: false,
		contentType: false,
		dataType:    'json',
		data:        form,
		success:     function(resp){
			console.log(resp);
			if (resp.status){
				$('.process').css('display','none');
				$('.complete').css('display','block');
				if ($('#mode').val()=='compress'){
					$('.complete .status').html(`Original size:&nbsp;&nbsp;&nbsp;${resp.origSize} B<br>Compressed size: ${resp.compSize} B<br>Time:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${resp.time} s`);
				} else {
					$('.complete .status').html(`Compressed size: ${resp.compSize} B<br>Original size:&nbsp;&nbsp;&nbsp;${resp.origSize} B<br>Time:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${resp.time} s`);
				}
				$('#dlink').attr('href',resp.dlink);
			} else {
				$('.process').css('display','none');
				$('.error').css('display','block');
			}
		}
	});
});

$('.closebtn').click(function(){
	$('.wrap').css('display','none');
	$('.process').css('display','none');
	$('.error').css('display','none');
	$('.complete').css('display','none');
});