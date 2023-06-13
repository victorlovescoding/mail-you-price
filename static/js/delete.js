let productData = document.getElementById("productData").textContent;
const form = document.querySelector("form");  
const deleteInput = document.getElementById("deleteInput");  
const deleteForm = document.getElementById("deleteForm");
let dataLength=0;
productData=productData.replaceAll("\"","'");
productData=productData.replaceAll("{'productName': '', 'productSite': ''}","");
productData=productData.replaceAll("{'","{\"");
productData=productData.replaceAll("'}","\"}");
productData=productData.replaceAll("':","\":");
productData=productData.replaceAll(": '",": \"");
productData=productData.replaceAll("', '","\", \"");
productData=productData.replaceAll("[,","[");
productData=productData.replaceAll(", ]"," ]");
productData=productData.replaceAll(", ,",",");

//用迴圈找出{的數量代表有幾筆資料
for(let num=0;num<productData.length;num++){
	if (productData[num]=="{"){
		dataLength+=1;         
	}   
}
console.log(productData);
productData = JSON.parse(productData);
getDataLength(productData,dataLength);

function getDataLength(productData,dataLength){
	if (dataLength!= "") {
		for (let num = 0; num < dataLength; num++) {
			const div = document.createElement("div");
			div.id="track";
			div.innerHTML = `
                <div id="productContainer">
                    <h4>${productData[num]["productName"]}</h4>
                    <a href="${productData[num]["productSite"]}">購物去</a>
                </div>
                <i class="fa-solid fa-trash"></i>
                `;
			form.appendChild(div);
			// const h4=document.querySelector("h4");

			div.addEventListener("click",()=>{
				if (confirm("確定要移除追蹤?")==true){
					let deleteItem=div.textContent;
					deleteInput.value=deleteItem;
					deleteForm.submit();
				}     
			});    
		}           
	}        
}  