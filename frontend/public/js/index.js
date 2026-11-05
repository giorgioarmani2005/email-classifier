
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
    try{
        let resp = await fetch(`http://${backend_host}:${backend_port}/api/v1/analyze/text`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({content: textarea.value}),
            credentials: "include",
        });

        if(!resp.ok){
            return null
        }
    
        return await resp.json()
    }
    catch(error){
        return null
    }
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

        this.is_analyzing = false
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
        if(this.is_analyzing){
            return
        }

        this.input.classList.remove('error')

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
        if(this.is_analyzing){
            return
        }

        if(this.input.classList.contains('error')){
            this.input.classList.remove('error')
            return
        }

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
        if(this.is_analyzing){
            return
        }
        if(!this.input.classList.contains("show-text")){
            return
        }
        this.button_cancel.disabled = true
        this.button_analyze.disabled = true
        this.button_analyze.innerText = "Анализируем...."
        this.textarea.readOnly = true;
        this.textarea.blur();
        this.textarea.style.pointerEvents = "none";
        
        this.is_analyzing = true
        let analyzed = await analyze_text(this.textarea.value)  
        this.is_analyzing = false
        if(analyzed !== null){
            this.set_result(this.textarea.value, analyzed)
        }
        else{
            this.input.classList.add('error')
        }

        this.button_cancel.disabled = false
        this.button_analyze.disabled = false  
        this.button_analyze.innerText = "Анализировать"
    }

    set_result(text, analyzed){
        if(this.is_analyzing){
            return
        }

        this.input.classList.remove('error')

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

        this.result.classList.remove('hidden')
        this.colored_words.style.display = "block"
        this.textarea.style.display = "none"
    }
}

class History {

    constructor(input_controller, history){
        this.input_controller = input_controller
        this.history = history
        this.records = {}
        this.error_loading = false
    }

    async update(){
        try{
            await this.update_ids()
            await this.get_what_changed()
            this.error_loading = false
        }
        catch(error){
            this.error_loading = true
        }
        this.render()
    }

    async get_ids(){
        let resp = await fetch(`http://${backend_host}:${backend_port}/api/v1/histories`, {
            method: "GET",
            credentials: "include",
        });

        if(!resp.ok){
            return null
        }

        return (await resp.json()).ids
    }

    async get_by_id(id){
        let resp = await fetch(`http://${backend_host}:${backend_port}/api/v1/history/${id}`, {
            method: "GET",
            credentials: "include",
        });

        if(!resp.ok){
            return null
        }

        return await resp.json()
    }

    async update_ids(){
        let ids = await this.get_ids()
        if(ids === null){
            this.error_loading = true
            return 
        }

        for(let i = 0; i < ids.length; i++){
            if(ids[i] in this.records){
                continue
            }
            this.records[ids[i]] = null
        }
    }

    async get_what_changed(){
        for(let id in this.records){
            if(this.records[id] === null){
                this.records[id] = await this.get_by_id(id)
            }
        }
    }

    render(){
        this.history.innerHTML = '<div class="title">История</div>'
        this.history.classList.remove('loading')
        if(this.error_loading){
            this.history.classList.add('error')
            return 
        }
        this.history.classList.remove('error')
        if(Object.keys(this.records).length == 0){
            this.history.classList.add('empty')
            return
        }
        this.history.classList.remove('empty')

        let sorted = Object.values(this.records).sort((r1, r2) => {
            
            if(this.record_is_invalid(r1) && this.record_is_invalid(r2)){
                return 0
            }
            if(this.record_is_invalid(r1)){
                return -1
            }
            if(this.record_is_invalid(r2)){
                return 1;
            }

            let r1_date = new Date(r1.date)
            let r2_date = new Date(r2.date)

            return r1_date - r2_date 
        })
        for(let record of sorted.reverse()){
            let elem = document.createElement('div')
            elem.classList.add('elem')

            if(this.record_is_invalid(record)){
                elem.classList.add('error')
                elem.innerText = "Ошибка загрузки";
                this.history.appendChild(elem)
                continue
            }

            let text = document.createElement('div')
            text.classList.add('text')
            text.innerText = this.format_text(record.content)
            
            let date = document.createElement('div')
            date.classList.add('date')
            date.innerText = this.format_date(record.date)

            elem.appendChild(text)
            elem.appendChild(date)

            elem.addEventListener("click", () => {
                this.input_controller.text_show(record.content, true)
                this.input_controller.set_result(record.content, record.analyzed)
                this.input_controller.input.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            })

            this.history.appendChild(elem)
        }
    }

    record_is_invalid(record){
        if(record === null){
            return true
        }
        if(record.date === null || record.analyzed === null || record.content === null){
            return true
        }
        return false
    }

    format_text(text){
        text = text.replaceAll('\n', ' ')
        if(text.length > 70){
            text = text.slice(0, 70) + '...'  
        }
        return text
    }

    format_date(date){
        date = new Date(date)
        let now = new Date()
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        let target = new Date(date.getFullYear(), date.getMonth(), date.getDate())

        let diff = Math.floor((today - target) / 86400000)

        if(diff === 0){
            return date.toLocaleTimeString("ru-RU")
        }

        if(diff === 1){
            return "вчера"
        }

        if(diff < 7){
            return date.toLocaleDateString("ru-RU", {weekday: "long"})
        }

        if(date.getFullYear() === now.getFullYear()){
            return date.toLocaleDateString("ru-RU", {day: "numeric", month: "long"})
        }

        return date.toLocaleDateString("ru-RU")
    }
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

let history_controller = new History(input_controller, history)





setTimeout(async () => {
    await history_controller.update()
}, 0)

setInterval(async () => {
    if(history_controller.error_loading){
        await history_controller.update()
    }
}, 3000)


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

document.addEventListener('keydown', (e) => {
    if(e.code == 'Escape'){
        input_controller.text_hide()
    }
    if(e.code == 'Tab'){
        e.preventDefault()
        history.classList.toggle("show")
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
    await history_controller.update()
})



