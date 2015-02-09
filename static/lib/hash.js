/* 
 * 哈希对象 
 *  
 * empty            清空hash。 
 * contains         检测hash是否包含此键值对，参数为key 
 * put              向hash增加一个键值对，参数两个，key与value 
 * get              根据key取得相应的value 
 * remove       根据key移除相应的键值对，返回修改后的hash 
 * pop              根据key移除相应的键值对，返回被移除的value 
 * keys             取得所有的键，以数组形式返回 
 * values           取得所有的值，以数组形式返回 
 * items            取得所有的键值对，以数组形式返回 
 * toObject         变成普通对象 
 * ensure       仅当此键不存在时才添加新的键值对 
 * forEach或each     类似Array.forEach，迭代执行传入函数 
 * map              类似Array.map，迭代执行传入函数，把执行结果放到一个新hash返回 
 * filter           类似Array.filter，迭代执行传入函数，把符合条件的键值对放到一个新hash返回 
 * toString         没什么好说的 
 */  
  
var Hash = function(obj) {  
    if (obj instanceof arguments.callee) return obj;  
    return new arguments.callee.fn.init(arguments);  
};  
Hash.fn = Hash.prototype = {  
    init: function(obj) {  
        var key = obj[0],  
        value = obj[1],  
        core = {},  
        toString = Object.prototype.toString,  
        i = 0;  
        if (obj.length === 2) { //如果有两个参数  
            core[key] = value;  
        } else {  
            if (toString.call(key) === '[object String]') {  
                key = key.replace(/^\s+|\s+$/g, ""); //进行trim操作  
                var arr = key.indexOf(",") !== -1 ? key.split(",") : key.split(/\s+/g);  
                while ((value = arr[i++])) core[value] = arr[i++];  
            } else if (toString.call(key) === '[object Array]') {  
                for (var i = 0, n = key.length; i < n; i++) core[i] = key[i]  
            } else {  
                core = key;  
            }  
        };  
        this.empty();  
        if (core) this.update(core);  
    },  
    empty: function() {  
        this._hash = {};  
        this.length = 0;  
        return this;  
    },  
    //用于初始化hash  
    //把普通对象的键值利用put方法传入_hash中,不考虑其prototype的成员  
    update: function(obj) {  
        for (var prop in obj) if (obj.hasOwnProperty(prop)) this.put(prop, obj[prop]);  
        return this;  
    },  
    contains: function(key) {  
        return this.get(key) !== void(0);  
    },  
    put: function(key, value) {  
        if (!this.contains(key)) { //如果没包含则  
            this.length++;  
        }  
        this._hash[key] = value;  
        return value;  
    },  
    //取得相应的值  
    get: function(key) {  
        return this._hash[key];  
    },  
    //移除一个键值对  
    remove: function(key) {  
        delete this._hash[key];  
        this.length--;  
        return this;  
    },  
    //移除指定的键值对，并返回对应的值  
    pop: function(key) {  
        var results = this.get(key);  
        this.remove(key);  
        return results;  
    },  
    //取得所有的键，以数组形式返回  
    keys: function() {  
        var keys = [],  
        obj = this._hash;  
        for (var prop in obj) if (obj.hasOwnProperty(prop)) keys.push(prop);  
        return keys;  
    },  
    //取得所有的值，以数组形式返回  
    values: function() {  
        var values = [],  
        obj = this._hash;  
        for (var prop in obj) if (obj.hasOwnProperty(prop)) values.push(obj[prop]);  
        return values;  
    },  
    //取得所有的键值对，以数组形式返回  
    items: function() {  
        var items = [],  
        obj = this._hash;  
        for (var prop in obj) if (obj.hasOwnProperty(prop)) items.push([prop, obj[prop]]);  
        return items;  
    },  
    //变成普通对象  
    toObject: function() {  
        return this._hash;  
    },  
    //仅当此键不存在时才添加，  
    ensure: function(key, value) {  
        var results = this.get(key);  
        if (results === void(0)) return this.put(key, value);  
        return results;  
    },  
    forEach: function(fn, bind) {  
        var pairs = this.items();  
        for (var i = 0, n = pairs.length; i < n; i++) {  
            fn.call(bind, pairs[i][1], pairs[i][0]);  
        }  
    },  
    map: function(fn, bind) {  
        var results = hash({});  
        this.each(function(value, key) {  
            results.put(key, fn.call(bind, value, key));  
        });  
        return results;  
    },  
    filter: function(fn, bind) {  
        var results = hash({});  
        this.each(function(value, key) {  
            if (fn.call(bind, value, key)) results.put(key, value);  
        });  
        return results;  
    },  
    index: function(val) { //与get方法相反，取得其key  
        var obj = this._hash;  
        for (var prop in obj) if (obj.hasOwnProperty(prop) && obj[prop] === val) return prop;  
        return null;  
    },  
    toString: function() {  
        var pairs = this.items(),  
        results = [];  
        for (var i = 0, n = pairs.length; i < n; i++) {  
            results[i] = pairs[i][0] + ":" + pairs[i][1]  
        }  
        return "{ " + results.join(", ") + " }";  
    },  
    each: this.forEach  
};  
Hash.fn.init.prototype = Hash.fn;  
