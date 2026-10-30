
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






function create_entry(id, result, score){
    let entry = document.createElement("div")

    span = document.createElement("span")
    span.innerHTML = id
    entry.appendChild(span)
    
    span = document.createElement("span")
    span.innerHTML = result
    entry.appendChild(span)
    
    span = document.createElement("span")
    span.innerHTML = score
    entry.appendChild(span)
    
    return entry
}





history = document.querySelector(".history")

setTimeout(async () => {
    let response = await fetch("http://localhost:8000/api/v1/histories", {
        method: "GET",
        headers: {
            "accept": "*/*"
        }
    });

    response = await response.json()
    let entries = response.histories_title

    for(let i = 0; i < entries.length; i++){
        console.log(entries[i])
        let entry = create_entry(entries[i].id, entries[i].result, entries[i].score)
        history.appendChild(entry)
    }
}, 0)






