	<?
		$q="SELECT * FROM $accTable where map_no != '' and server_id= $registrar ";
		$q.=$search;
		$q.=" ORDER BY rly_no DESC";
		//print $q;
		$sn=1; 
	?>
	<div >
		<div class="sticky w3-bar ">
		  <div class="w3-bar-item w3-xxlarge" style="text-transform:uppercase;color:#18303c;text-transform:bold;font-family: 'Trebuchet MS';">Short Codes</b></div>
		</div>
		<div class="sticky w3-bar ">
		  <i class="w3-small w3-text-grey w3-padding" ><? print $regName." Exchange (IP: ". $primaryIP.")   / [". $divn1." division /". $rly1."]"; ?></i>
		  <!--div class="w3-bar-item w3-right" onclick="window.print()"><i class="fa fa-print w3-text-green  w3-large"></i></div-->
		  <div class="w3-bar-item w3-right w3-tiny" onclick="addPages('0','acc','<? print $_GET['acc_type'];?>','nil');"><button class="w3-button w3-border w3-round w3-border-green w3-text-green  w3-hover-green"><i class="fa fa-plus-circle w3-tiny " aria-hidden="true"> CREATE</i> </button></div>
		</div>
				
			<table class="w3-table w3-small w3-card  w3-half" style="background:white;word-break:keep-all;">
				<tr class=" w3-small w3-text-blue w3-opacity w3-bold"  style="text-align:left;" valign="top">
					<th width="10%">S.N</th>
					<th width="35%" style="text-transform:uppercase;border-left:1px solid white">Short Code</th> 
					<th width="35%" style="text-transform:uppercase;border-left:1px solid white">Name</th>
					<th width="20%" style="text-transform:uppercase;border-left:1px solid white"  class="w3-center"><i class="fa fa-list-ul" aria-hidden="true"></i></th>
				</tr>
				<? 		
				$s=mysqli_query($conn,$q);
				//print mysqli_error($conn);
				if(!(!$s) || mysqli_num_rows($s)>0){
				while($d=mysqli_fetch_assoc($s)){ 
				?>
				<tr  valign="top"  class="w3-hover-light-grey" style="background:<? print $rowColor[$d["acc_type"]];?> ;text-align:left;height:50px;text-transform:capitalize;">
					<td width="10%">
						(<? print $sn;$sn++?>)</td>
		
					<td width="35%" style="text-transform:uppercase;border-left:1px solid #F8F9F9">
						<? print $d['map_no'];?>
					</td>
					
					<td width="35%" style="text-transform:uppercase;border-left:1px solid #F8F9F9">
						<? print $d['acc_name'];?>
					</td>
					
					<td width="20%" style="text-transform:capitalize;border-left:1px solid #F8F9F9;" class="w3-center">
						<? if ($user_type=="admin" ||  $userid==$owner){ ?>
						<i class="fa fa-pencil-square-o w3-large w3-text-blue" aria-hidden="true" alt="Edit" title="Edit" onclick="addPages('1','acc','<? print $_GET['acc_type'];?>','<? print $d['id'];?>');"></i>
						<? } ?>
					</td>
				</tr>
	<?		}
		}
			 ?>
			</table>
		  </div>
		 <br><br>