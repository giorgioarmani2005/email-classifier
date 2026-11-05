
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
    const count = 2000

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



let background = document.querySelector(".background")


generate_stars(background)
