
function print(to_print){
    console.log(to_print)
}

/************************  Рамачка  ************************************/   
/**/                                                                 /**/
/**/  function add_text_to_node(node, text){                         /**/                            
/**/      let splited = text.split("\n")                             /**/
/**/      for(let i = 0; i < splited.length; i++){                   /**/
/**/          if(i != 0){                                            /**/
/**/              node.appendChild(document.createElement('br'))     /**/
/**/          }                                                      /**/
/**/          node.appendChild(document.createTextNode(splited[i]))  /**/
/**/      }                                                          /**/
/**/  }                                                              /**/
/**/                                                                 /**/
/***********************************************************************/  

function isspace(str){
    return str.length > 0 && /^\s+$/.test(str)
}

function random(from, to){
    return Math.random() * (to - from) + from
}


function get_diamond(HEIGHT, WIDTH){
    const h = random(-HEIGHT/2, HEIGHT/2);
    const maxW = WIDTH/2 * (1 - 2 * Math.abs(h) / HEIGHT);

    const sign = Math.random() < 0.5 ? -1 : 1;
    const edge = Math.random() ** 0.7;

    const w = sign * maxW * random(edge, 1);

    return {h: h, w: w};    
}

function generate_stars(background_node){
    const count = 300

    for(let i = 0; i < count; i++){
        let star = document.createElement("div")
        let diamond = get_diamond(65, 30)

        star.classList.add("star")
        if(i > 0.125*count){
            star.classList.add("form")
            star.style.setProperty("--size", `${random(0.2, 0.8)}`)
        }
        else{
            star.style.setProperty("--size", `${random(0.1, 0.6)}`)
        }
        star.style.setProperty("--color", `var(--star_color${Math.floor(random(0, 3))})`)
        star.style.setProperty("--shift", `${random(0, 6) - 6}s`)
        
        if(i > 0.12*count && i < 0.8*count){
            star.style.setProperty("--x_f", `calc(${diamond.w*8}px + 50%)`)
            star.style.setProperty("--y_f", `calc(${diamond.h*8}px + 50%)`)
        }
        if(i >= 0.8*count && i < 0.9*count){
            star.style.setProperty("--x_f", `calc(${diamond.w*2}px + 50% - 200px)`)
            star.style.setProperty("--y_f", `calc(${diamond.h*2}px + 50% + 120px)`)
        }
        if(i >= 0.9*count){
            star.style.setProperty("--x_f", `calc(${diamond.w*2}px + 50% + 200px)`)
            star.style.setProperty("--y_f", `calc(${diamond.h*2}px + 50% + 120px)`)
        }
        
        if(diamond.w > 0){
            star.style.setProperty("--x", `${random(50, 100)}%`)
        }
        else{
            star.style.setProperty("--x", `${random(0, 50)}%`)
        }
        if(diamond.h > 0){
            star.style.setProperty("--y", `${random(50, 100)}%`)
        }
        else{
            star.style.setProperty("--y", `${random(0, 50)}%`)
        }
        
        background.appendChild(star)
    }
}

async function analyze_text(text){
    let resp = await fetch(`http://${backend_host}:${backend_port}/api/v1/analyze/text`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({content: textarea.value}),
        credentials: "include",
    });

    return await resp.json()
}



class Input {
    constructor(input, textarea, button_cancel, button_analyze, result){
        this.input = input
        this.textarea = textarea
        this.button_cancel = button_cancel
        this.button_analyze = button_analyze
        this.result = result
        
        this.res_triage = result.querySelector(".triage")
        this.res_priority = result.querySelector(".priority")
        this.res_risk = result.querySelector(".risk")
        this.res_should_process = result.querySelector(".should-process")
        this.colored_words = input.querySelector(".colored-words")
        

        this.button_cancel.disabled = true
        this.button_analyze.disabled = true
    }

    parse_eml(content){
        content = content.split("\r\n\r\n")
        if(content.length < 2){
            content = content[0].split("\n\n")
        }
        if(content.length < 2){
            return content[0]
        }
        content = content[1].replaceAll("\r\n", "").replaceAll("\n", "")

        content = content.split("<")
        for(let i = 1; i < content.length; i++){
            let splited = content[i].split(">")
            if(splited.length < 2){
                continue;
            }
            content[i] = splited[1]
            if(splited[0].includes("br")){
                content[i] = "\n" + content[i]
            }
        }

        content = content.join("")
        return content
    }

    text_show(content_to_show = null, plain_text = true){
        this.result.classList.add('hidden')
        this.input.classList.add('show-text')
        this.button_cancel.disabled = false
        this.button_analyze.disabled = false
        if(content_to_show != null){
            if(!plain_text){
                content_to_show = this.parse_eml(content_to_show)
            }
            this.textarea.value = content_to_show
        }
    }

    text_hide(){
        this.result.classList.add('hidden')
        this.input.classList.remove('show-text')
        this.button_cancel.disabled = true
        this.button_analyze.disabled = true
        this.textarea.value = ''
        this.textarea.readOnly = false;
        this.textarea.style.pointerEvents = "auto";
        this.colored_words.style.display = "none"
        this.textarea.style.display = "block"
    }

    async analyze(){
        if(!this.input.classList.contains("show-text")){
            return
        }
        this.result.classList.add('hidden')
        this.button_cancel.disabled = true
        this.button_analyze.disabled = true
        this.button_analyze.innerText = "Анализируем...."
        this.textarea.readOnly = true;
        this.textarea.blur();
        this.textarea.style.pointerEvents = "none";
        let analyzed = await analyze_text(this.textarea.value)  
        
        this.set_result(this.textarea.value, analyzed)

        this.button_cancel.disabled = false
        this.button_analyze.disabled = false  
        this.button_analyze.innerText = "Анализировать"

        this.result.classList.remove('hidden')
        this.colored_words.style.display = "block"
        this.textarea.style.display = "none"
    }

    set_result(text, analyzed){
        setTimeout(() => {
            this.res_triage.style.setProperty("--len", `${analyzed.triage_confidence}`)
            this.res_priority.style.setProperty("--len", `${analyzed.priority_confidence}`)
            this.res_risk.style.setProperty("--len", `${analyzed.risk_confidence}`)
            this.res_should_process.style.setProperty("--len", `${analyzed.should_process_confidence}`)
        }, 400)

        this.res_triage.querySelector(".value").innerText = analyzed.triage
        this.res_priority.querySelector(".value").innerText = analyzed.priority
        this.res_risk.querySelector(".value").innerText = analyzed.risk
        this.res_should_process.querySelector(".value").innerText = analyzed.should_process

        this.colored_words.innerHTML = ""
        let content = text.split(" ")
        let cur_word_index = 0

        for(let i = 0; i < content.length; i++){
            if(i != 0){
                content[i] = " " + content[i]
            }
            
            if(content[i] == "" || isspace(content[i])){
                add_text_to_node(this.colored_words, content[i])
                continue
            }

            if(analyzed.shap_indices.includes(cur_word_index)){
                let cur_node = document.createElement("span")
                cur_node.textContent = content[i]
                cur_node.classList.add("highlight")
                this.colored_words.appendChild(cur_node)
            }
            else{
                add_text_to_node(this.colored_words, content[i])
            }

            cur_word_index++
        }
    }
}

class History {
    // record = {
    //     id: 0,
    //     date: "" | null,
    //     content: "asda" | null,
    //     analyze: | null ...
    // }

    constructor(history){
        this.history = history
        this.records = []
    }

    async update(){

    }

    async get_ids(){
        let resp = await fetch(`http://${backend_host}:${backend_port}/api/v1/histories`, {
            method: "GET",
            credentials: "include",
        });
        return (await resp.json()).ids
    }

    async get_by_id(id){
        let resp = await fetch(`http://${backend_host}:${backend_port}/api/v1/history/${id}`, {
            method: "GET",
            credentials: "include",
        });
        return await resp.json()
    }

    async update_ids(){
        let ids = this.get_ids()
        for(let i = 0; i < ids.length; i++){
            if(!this.records.some((record) => {return record.id == ids[i]})){
                this.records.push({
                    id: ids[i],
                    date: null,
                    content: null,
                    analyze: null
                })
            }
        }
    }

    async get_what_changed(){
        for(let i = 0; i < this.records.length; i++){
            if(this.records[i].date == null && this.records[i].analyzed == null && this.records[i].content == null){
                this.records[i] = this.get_by_id(this.records[i].id)
            }
        }
    }

    render(){
        this.history.innerHTML = ""
        for(let i = 0; i < this.records.length; i++){
            let elem = document.createElement("div")
            elem.classList.add("elem")
            
            let text = document.createElement("div")
            text.classList.add("text")
            text.innerText = this.records[i].content
            let date = document.createElement("div")
            date.classList.add("date")
            date.innerText = this.format_date(this.records[i].date)

            elem.appendChild(text)            
            elem.appendChild(date)            
        }
    }

    format_date(date){
        date = Date(date)

        let yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1); 

        return date.toLocaleDateString("ru-RU", {
            year, month, day, hour, minute
        })
    }

//   Параметр	Значения	Результат
//   weekday	"long"	    четверг
// 	             "short"	 чт
// 	             "narrow"	Ч
//    era	     "long"	  от Рождества Христова
// 	             "short"	н. э.
// 	             "narrow"	н. э.
// year	        "numeric"	  2026
// 	             "2-digit"	   26
// month	    "numeric"	   11
// 	              "2-digit"	   11
// 	              "long"	   ноября
// 	              "short"	   нояб.
// 	              "narrow"	   Н
// day	           "numeric"	5
// 	                "2-digit"	05

// Параметр	 Значения	Результат
// hour	    "numeric"	      14
// 	        "2-digit"	      14
// minute	"numeric"	   30
// 	        "2-digit"	   30
// second	"numeric"	   45
// 	       "2-digit"	   45
// dayPeriod	"long"	дня
// 	           "short"	дня
// 	           "narrow"	д
}








let background = document.querySelector(".background")
let input = document.querySelector('.input')
let text = input.querySelector('.text')
let textarea = text.querySelector('textarea')
let file_input = input.querySelector('#file-input')
let button_cancel = document.querySelector('button.cancel')
let button_analyze = document.querySelector('button.analyze')
let result = document.querySelector('.result')
let history_button = document.querySelector('header .history')
let history = document.querySelector('.side-bar')


generate_stars(background)

let input_controller = new Input(input, textarea, button_cancel, button_analyze, result)






history_button.addEventListener("click", () => {
    history.classList.toggle("show")
})

document.addEventListener("click", (e) => {
    if(e.target.closest(".dont-hide-history")) {
        return;
    }
    history.classList.remove("show")
})

window.addEventListener('scroll', () => {
    if(window.scrollY > 100){
        background.classList.remove('formed')
    }
    else{
        background.classList.add('formed')
    }
})

text.addEventListener('input', () => {
    if(textarea.value == ''){
        input_controller.text_hide()
        return
    }
    input_controller.text_show()
})

text.addEventListener('keydown', (e) => {
    if(e.code == 'Escape'){
        input_controller.text_hide()
    }
})

file_input.addEventListener('change', async () => {
    let file = file_input.files[0]
    if(!file){
        return
    }
    let text = await file.text()
    let ext = file.name.split('.').pop().toLowerCase()
    input_controller.text_show(text, ext != 'eml')
})

button_cancel.addEventListener("click", () => {
    input_controller.text_hide()
})

document.addEventListener("paste", async (e) => {
    for(const item of e.clipboardData.items){
        if(item.kind === "file"){
            const file = item.getAsFile();
            let text = await file.text()
            let ext = file.name.split('.').pop().toLowerCase()
            input_controller.text_show(text, ext != 'eml')
            return
        }
    }
})

input.addEventListener("dragover", (event) => {
    event.preventDefault();
});

input.addEventListener("drop", async (event) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    for(const file of files){
        const text = await file.text();
        let ext = file.name.split('.').pop().toLowerCase()
        input_controller.text_show(text, ext != 'eml')
    }
});

button_analyze.addEventListener("click", async () => {
    await input_controller.analyze()
})




// button_analyze.addEventListener("click", async () => {
//     let response = await fetch("http://localhost:8000/api/v1/analyze/text", {
//         method: "POST",
//         headers: {
//             "accept": "*/*",
//             "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//             content: textarea.value,
//         })
//     });

//     response = await response.json();

//     if(response.status == "success"){
//         textarea.value = "success"
//     }
//     else{
//         textarea.value = "error"
//     }
// })








