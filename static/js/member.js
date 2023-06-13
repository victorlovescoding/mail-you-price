if (window.history.replaceState) {
	window.history.replaceState( null, null, window.location.href );
}
let productData = document.getElementById("productData").textContent;
const deleteInput = document.getElementById("deleteInput");  
const deleteForm = document.getElementById("deleteForm");
let dataLength=0;
const trackContainer = document.getElementById("trackContainer");
productData=productData.replaceAll("\"","'");
productData=productData.replaceAll("{'","{\"");
productData=productData.replaceAll("'}","\"}");
productData=productData.replaceAll("':","\":");
productData=productData.replaceAll(": '",": \"");
productData=productData.replaceAll("', '","\", \"");

//用迴圈找出{的數量代表有幾筆資料
for(let num=0;num<productData.length;num++){
	if (productData[num]=="{"){
		dataLength+=1;         
	}   
}
// window.addEventListener("load",(e)=>{
// 	const form = document.querySelectorAll("form");
// 	const input = document.querySelectorAll("input");
  
// });

productData = JSON.parse(productData);
getDataLength(productData,dataLength);

function getDataLength(productData,dataLength){
	if (dataLength!= "") {
		for (let num = 0; num < dataLength; num++) {
			const div = document.createElement("div");
			div.id="track";
			div.innerHTML = `
            <h4>${productData[num]["productName"]}</h4>
            <hr>
            <a href="${productData[num]["productSite"]}">購物去</a>
          `;
			trackContainer.appendChild(div);
			// const h4=document.querySelector("h4");

			div.addEventListener("dblclick",()=>{
				if (confirm("確定要移除追蹤?")==true){
					let deleteItem=div.textContent;
					deleteInput.value=deleteItem;
					deleteForm.submit();
				}     
			});    
		}           
	}        
} 