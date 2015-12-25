var KEY_USER = "username-myx9x091";
var KEY_PWD = "pwd-ucuaksdf";
var KEY_HOST = "HOST";
var KEY_MEANING = "KEY_MEANING";
var last_get_timetamp = 0;
host = getHost();
meanings = {}
store.set(KEY_HOST, host);

function getHost(){
    return store.get(KEY_HOST);
}

function getUser(){
    var user = store.get(KEY_USER);
    return user;
}

function getPwd(){
    var pwd = store.get(KEY_PWD);
    return pwd;
}

function getUserInfo(){
    var rst = {
        host: getHost(),
        user: getUser(),
        pwd: getPwd(),
    }
    return rst;
}

function oldWordMap(){
    return store.getAll();
}

var warningId = 'notification.warning';

function hideWarning(done) {
  chrome.notifications.clear(warningId, function() {
    if (done) done();
  });
}

function clear(){
    store.clear();
    last_get_timetamp = 0;
}

function notify(message) {
  hideWarning(function() {
    chrome.notifications.clear(warningId, function() {});
    var ntf = chrome.notifications.create(warningId, {
      iconUrl: chrome.runtime.getURL('images/icon-48.png'),
      title: '提示',
      type: 'basic',
      message: message,
      //buttons: [{ title: 'Learn More' }],
      isClickable: true,
      priority: 2,
    }, function() {});

    setTimeout(function () {
          chrome.notifications.clear(warningId, function() {})}
        ,3000);
  });
}

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse){
    console.log("后台收到命令:" + message);
    var response = null;

    if (message == "getUserInfo"){
        response = getUserInfo();
    }

    if (message == "getAllWords"){
        if(is_ignore_url(sender.url)){
            response = null;
        }else if(!isLogin()){
            notify("当前未登陆单词变色");
            response = null;
        }else {
            getAllWords(function(rep){});
            response = oldWordMap();
        }
    }

    if (message == "clear"){
        clear();
        response = "ok";
    }

    if (message.startsWith("start###")){
        var ifStart = message.split("###")[1] == "true"
        store.set("start###", ifStart)
        response = "ok"
    }

    if (message.startsWith("getClzName")){
        var word = message.split("###")[1];

        var change2new = changeWord2New(word);
        response = change2new;
    }

    if (message.startsWith("setUserInfo")){
        var infos = message.split("###");
        var host = infos[1];
        var user = infos[2];
        var pwd = infos[3];
        store.set(KEY_HOST, host);
        store.set(KEY_USER, user);
        store.set(KEY_PWD, pwd);
        getAllWords(function(rep){});
        response = "ok"
    }

    if (message.startsWith("refreshWordMeaning")){
        var words = message.split("###")[1];
        getAllMeaning(words);
        response = "ok"
    }

    if (message.startsWith("getMeaning")){
        var word = message.split("###")[1];
        var key = word;
        response = meanings[key];
    }
    console.log("后台收到命令:" + message + "\n 返回数据:" + response);
    sendResponse(response);
});

function isLogin(){
    var user = store.get(KEY_USER);
    var pwd = store.get(KEY_PWD);
    return user != null && pwd != null ;
}


function getAllWords(func){
    //last_get_timetamp = 0;
    var host = getHost();
    var curUrl = host + "/get_words";
    request_param = {"user": getUser(), "pwd": getPwd(), 
        "last_get_timetamp": last_get_timetamp};
    $.get(curUrl,
            request_param,
            function(result) {
                var jo = $.parseJSON(result);
                if(jo.status != "ok"){
                    func(null);
                }
                last_get_timetamp = jo.timestamp;
                var words = jo.result;

                if(jo.result.length > 0){
                    wordCount = store.length
                    var msg = "更新了 " + jo.result.length + " 个单词" ;
                    notify(msg);
                }
                
                var split_word_list = jo.result;
                for(var i=0; i<split_word_list.length; i++){
                    var curWord = split_word_list[i].spelling;
                    store.set(curWord, split_word_list[i]);
                }
                console.log("refresh words....");
                if (func){func("")};
            }
    ).fail(function(){
        if (func){func(oldWordMap)};
    });
}


function getAllMeaning(words){
    var ws = words.split("#");
    words = [];
    for(var i=0; i<ws.length; i++){
        var key = ws[i];
        if(!(key in meanings)){
            words.push(key);
        }

    }
    var host = getHost();
    var reqUrl = host + "/get_words_meaning";
    console.log('request url ==>' + reqUrl)
     $.post(reqUrl, {"user": getUser(), "pwd": getPwd(), "words": words},
            function(response){
            console.log('response ==>' + response.toString())
            if(response.status == "ok"){
                for(var k in response.result){
                    meanings[k] = response.result[k];
                }
                
            }
            console.log("此页加载完成。");
    }, 'json');
}

function changeWord2New(spelling) {
    var change2new = false;
    if(store.get(spelling) != null){
        var curWord = store.get(spelling)
        change2new = curWord.status == 1;

    }else{
        change2new = false;
    }

    var user = store.get(KEY_USER);
    var pwd = store.get(KEY_PWD);
    var host = getHost();
    var status = change2new ? "new" : "old";
    var reqUrl = host + "/set_word_status/" + spelling + "/" + status;
     $.get(reqUrl, {"user": user, "pwd": pwd },
            function(result){
            getAllWords();
    });
    return change2new;
}

if(getUser() != null && getPwd() != null){
   getAllWords();
}


function tran_this_page(infos, tab){
    dont_ignore_url(infos.pageUrl);
}

function dont_tran_this_page(infos, tab){
    ignore_url(infos.pageUrl);
}

chrome.contextMenus.create(
    {
        type: "normal",
        title: "单词变色",
        id: 'main2',
        contexts: ['all']
    }
)

chrome.contextMenus.create(
    {
        type: "normal",
        title: "不翻译此页",
        id: 'nottran',
        parentId: 'main2',
        onclick: dont_tran_this_page
    }
)

chrome.contextMenus.create(
    {
        type: "normal",
        title: "翻译此页",
        id: 'tran',
        parentId: 'main2',
        onclick: tran_this_page
    }
)