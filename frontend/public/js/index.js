
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




let background = document.querySelector(".background")

const stars_cnt = 300

for(let i = 0; i < stars_cnt; i++){
    let star = document.createElement("div")

    star.classList.add("star")
    if(i > 0.125*stars_cnt){
        star.classList.add("form")
        star.style.setProperty("--size", `${random(0.2, 0.8)}`)
    }
    else{
        star.style.setProperty("--size", `${random(0.1, 0.6)}`)
    }
    star.style.setProperty("--color", `var(--star_color${Math.floor(random(0, 3))})`)
    star.style.setProperty("--shift", `${random(0, 6) - 6}s`)
    diamond = get_diamond(65, 30)
    
    if(i > 0.12*stars_cnt && i < 0.8*stars_cnt){
        star.style.setProperty("--x_f", `calc(${diamond.w*8}px + 50%)`)
        star.style.setProperty("--y_f", `calc(${diamond.h*8}px + 50%)`)
    }
    if(i >= 0.8*stars_cnt && i < 0.9*stars_cnt){
        star.style.setProperty("--x_f", `calc(${diamond.w*2}px + 50% - 200px)`)
        star.style.setProperty("--y_f", `calc(${diamond.h*2}px + 50% + 120px)`)
    }
    if(i >= 0.9*stars_cnt){
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



window.addEventListener('scroll', () => {
    if(window.scrollY > 100){
        background.classList.remove('formed')
    }
    else{
        background.classList.add('formed')
    }
})


input = document.querySelector('.input')
text = input.querySelector('.text')
textarea = text.querySelector('textarea')
file_input = input.querySelector('#file-input')
button_cancel = document.querySelector('button.cancel')
button_analyze = document.querySelector('button.analyze')



button_cancel.disabled = true
button_analyze.disabled = true

function text_on(){
    input.classList.add('show-text')
    button_cancel.disabled = false
    button_analyze.disabled = false
}

function text_off(){
    input.classList.remove('show-text')
    button_cancel.disabled = true
    button_analyze.disabled = true
    textarea.value = ''
    input.classList.remove('success')
    input.classList.remove('error')
}




text.addEventListener('input', () => {
    text_on()
})

text.addEventListener('keydown', (e) => {
    if(e.code == 'Escape'){
        text_off()
    }
})

file_input.addEventListener('change', async () => {
    let file = file_input.files[0]
    if(!file){
        return
    }
    let text = await file.text()
    textarea.value = text
    text_on()
})

button_cancel.addEventListener("click", () => {
    text_off()
})

document.addEventListener("paste", async (e) => {
    for(const item of e.clipboardData.items){
        if(item.kind === "file"){
            const file = item.getAsFile();
            let text = await file.text()
            textarea.value = text
            text_on()
        }
    }
})

input.addEventListener("dragover", (event) => {
    event.preventDefault();
});

input.addEventListener("drop", async (event) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    for (const file of files) {
        const text = await file.text();
        textarea.value = text
        text_on()
    }
});





button_analyze.addEventListener("click", async () => {
    let response = await fetch("http://localhost:8000/api/v1/analyze/text", {
        method: "POST",
        headers: {
            "accept": "*/*",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            content: textarea.value,
        })
    });

    response = await response.json();

    if(response.status == "success"){
        textarea.value = "success"
    }
    else{
        textarea.value = "error"
    }
})








