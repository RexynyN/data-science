
function downloadBlob(blob) {
    // // Convert your blob into a Blob URL (a special url that points to an object in the browser's memory)
    // const blobUrl = URL.createObjectURL(blob);

    // Create a link element
    const link = document.createElement("a");

    const filename = blob.split("/");
    // Set link's href to point to the Blob URL
    link.href = blob;
    link.download = filename[filename.length - 1] + ".jpg";

    // Append link to the body
    document.body.appendChild(link);

    // Dispatch click event on the link
    // This is necessary as link.click() does not work on the latest firefox
    link.dispatchEvent(
        new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        })
    );

    // Remove link from body
    document.body.removeChild(link);
}

async function getBlobs(){
    // A Thread.sleep lookalike
    async function sleep(msec){
        return new Promise(resolve => setTimeout(resolve, msec));
    }

    // Range for the for loop (lol)
    function range (stop){
        let start = 0;
        return Array.from({ length: (stop - start) },(value, index) => start + index);
    }

    let x = window.innerWidth * 3/4;
    let y = window.innerHeight * 1/2; 
    


    const pages = Number(document.getElementsByClassName("page-number")[1].innerHTML)
    let blobs = [];
    for(let _ of range(pages)) {
        let blob = document.getElementsByClassName("img sp limit-width limit-height mx-auto")[0].src;
        blobs.push(blob)
        document.elementFromPoint(x, y).click();
        sleep(500);
    }

    return blobs
}

await getBlobs()


// downloadBlob(imageBlob);


function click(x, y)
{
    var ev = new MouseEvent('click', {
        'view': window,
        'bubbles': true,
        'cancelable': true,
        'screenX': x,
        'screenY': y
    });

    var el = document.elementFromPoint(x, y);

    el.dispatchEvent(ev);
}

let x = 1625;
let y = 215;
click(x, y);

