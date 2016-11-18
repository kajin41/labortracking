/**
 * Created by gmercado on 11/18/2016.
 */
$(".filter").change(function (){
  if (this.val() == "open"){
      document.getElementsByName("From").style.display = 'none';
  }
}
);