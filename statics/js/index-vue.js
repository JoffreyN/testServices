var host=document.location.host;

Date.prototype.Format = function (fmt) { // author: meizz
  var o = {
    "M+": this.getMonth() + 1, // 月份
    "d+": this.getDate(), // 日
    "h+": this.getHours(), // 小时
    "m+": this.getMinutes(), // 分
    "s+": this.getSeconds(), // 秒
    "q+": Math.floor((this.getMonth() + 3) / 3), // 季度
    "S": this.getMilliseconds() // 毫秒
  };
  if (/(y+)/.test(fmt))
    fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
  for (var k in o)
    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]):(("00" + o[k]).substr(("" + o[k]).length)));
      return fmt;
};

function getFormatTime(){
    return new Date().Format("yyyy-MM-dd hh:mm:ss.S");
};

String.prototype.format = function(args) {
  if (arguments.length > 0) {
    var result = this;
    if (arguments.length == 1 && typeof(args) == "object") {
      for (var key in args) {
        var reg = new RegExp("({" + key + "})", "g");
        result = result.replace(reg, args[key]);
      }
    } else {
      for (var i = 0; i < arguments.length; i++) {
        if (arguments[i] == undefined) {
          return "";
        } else {
          var reg = new RegExp("({[" + i + "]})", "g");
          result = result.replace(reg, arguments[i]);
        }
      }
    }
    return result;
  } else {
    return this;
  }
};

function getLayout() {
var layout_func = [
    {"i":"0","id":"card0","t":"重置密码","ele":`
<table>
    <tr>
        <td><label>重置方式:</label></td>
        <td><label>选择环境:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="resetType"><option value="APP">APP</option><option value="BOSS">BOSS</option><option value="CGF">陈广峰的Services</option></select></td>
        <td class="select no-drag"><select id="env3"><option value="test">TEST</option><option value="uat">UAT</option><option value="dev">DEV</option></select></td>
    </tr>
    <tr>
        <td><label>输入账户:</label></td>
        <td><label>输入新密码:</label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="name3" value="" placeholder="空格分隔" title="批量功能仅支持TTL账户"></td>
        <td class="no-drag"><input type="text" class="input_text" id="pword3" value="aaaa1111"></td>
    </tr>
    <tr>
        <td class="no-drag" colspan="2"><button id="button3" class="waves bg_color2">点击重置</button></td>
    </tr>
</table>`},
    {"i":"1","id":"card1","t":"解锁账户","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>输入账户:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env7"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="name7" placeholder="必填"></td>
        <td class="no-drag"><button id="button7" class="waves bg_color2">点击解锁</button></td>
    </tr>
</table>`},
    {"i":"2","id":"card2","t":"资金存入|提取","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>选择币种:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env4"><option value="test">TEST</option><option value="uat">UAT</option><option value="dev">DEV</option></select></td>
        <td class="select no-drag" id="currency">
            <select class="selects" multiple="multiple">
                <option value="hkd">HKD</option>
                <option value="usd">USD</option>
                <option value="cny">CNY</option>
            </select>
        </td>
    </tr>
    <tr>
        <td><label>输入账户:</label></td>
        <td><label>输入金额:</label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="name4" value="" placeholder="空格分隔"></td>
        <td class="no-drag"><input type="number" class="input_text" id="money" value="100000" max="100000000" onblur="javascript:if (this.value>100000000){alert('金额不能大于1亿');this.value=100000000;}"></td>
    </tr>
    <tr>
        <td class="no-drag" colspan="2"><button class="waves bg_color2" id="button4">存入并审核</button></td>
    </tr>

</table>`},
    {"i":"3","id":"card3","t":"股票|基金|债券|结构化产品 持仓","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>市场类型:</label></td>
        <td><label>输入账户:</label></td>
    <tr>
    <tr>
        <td class="select no-drag"><select id="env9"><option value="test">TEST</option><option value="uat">UAT</option><option value="dev">DEV</option></select></td>
        <td class="select no-drag">
            <select id="markettype">
                <option value="HKG">HKG</option>
                <option value="USA">USA</option>
                <option value="SHA">SHA</option>
                <option value="SZA">SZA</option>
                <option value="FUND">基金</option>
                <option value="BOND">债券</option>
                <option value="SPMK">结构化</option>
            </select>
        </td>
        <td class="no-drag"><input type="text" class="input_text" id="name9" value="" placeholder="空格分隔"></td>
    </tr>
    </tr>
        <td><label>产品代码:</label></td>
        <td><label>输入数量:</label></td>
        <td></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="stockcode" placeholder="00700" title="基金请输入 ProductCode ,如: MLU1342487771USD"></td>
        <td class="no-drag"><input type="text" class="input_text" id="stocknum" placeholder="10000"></td>
        <td class="no-drag"><button id="button9" class="waves bg_color2">点击执行</button></td>
    </tr>
</table>`},
    {"i":"4","id":"card4","t":"银证入金","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>银行类型:</label></td>
        <td><label>选择币种:</label></td>
        <td><label>证券账户:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env15"><option value="test">TEST</option><option value="uat">UAT</option><option value="dev">DEV</option></select></td>
        <td class="select no-drag"><select id="bankName"><option value="港分银行">港分银行</option><option value="永隆银行">永隆银行</option><option value="民生银行">民生银行</option></select></td>
        <td class="select no-drag" id="currency15">
            <select class="selects fbankSec" multiple="multiple">
                <option value="hkd">HKD</option>
                <option value="usd">USD</option>
                <option value="cny">CNY</option>
            </select>
        </td>
        <td class="no-drag"><input type="text" class="input_text" id="name15" value="" placeholder="必填"></td>
    </tr>
    <tr>
        <td><label>银行账户号码:</label></td>
        <td><label>输入金额:</label></td>
        <td><label>交易日期:</label></td>
        <td rowspan="2" class="td_checkbox no-drag" id="tip15_1">
            <label><input type="checkbox" id="bankReg"><span id="bankReg_desc">自动登记</span></label><br>
            <label><input type="checkbox" id="addBank" checked="checked" disabled><span id="addBank_desc" class="gray">自动添加结算卡</span></label>
        </td>
    </tr>
    <tr>
        <td class="no-drag"><input type="number" class="input_text" id="bankNum" placeholder="必填"></td>
        <td class="no-drag"><input type="number" class="input_text" id="money15" value="100000" max="100000000" onblur="javascript:if (this.value>100000000){alert('金额不能大于1亿');this.value=100000000;}"></td>
        <td class="no-drag"><input type="date" class="input_text" id="tradeDate" value="" placeholder="20211103"></td>
        <td class="no-drag"><button id="button15" class="waves bg_color6">点击执行</button></td>
    </tr>
</table>`},
    {"i":"5","id":"card5","t":"查询测试账户","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>查询数量:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env5"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="number" class="input_text" id="input5" value="10"></td>
        <td class="no-drag"><button class="waves bg_color2" id="button5" @click="getTestAccount">点击查询</button></td>
    </tr>
</table>`},
    {"i":"6","id":"card6","t":"添加新股","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>新股名称:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env16"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="newStockname" placeholder="为空随机生成"></td>
    </tr>
    <tr>
        <td><label>新股代码:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="number" class="input_text" id="newStockcode" placeholder="为空随机生成"></td>
        <td class="no-drag"><button class="waves bg_color6" id="button16">点击执行</button></td>
    </tr>
</table>`},
    {"i":"7","id":"card7","t":"session 失效","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>输入账户:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env17"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="name17" placeholder="必填"></td>
    </tr>
    <tr>
        <td><label>sessionID:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="sessionid" placeholder="必填"></td>
        <td class="no-drag"><button class="waves bg_color6" id="button17">点击执行</button></td>
    </tr>
</table>`},
    {"i":"8","id":"card8","t":"结单推送","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>输入账户:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env18"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="name18" placeholder="必填"></td>
    </tr>

    <tr>
        <td><label>结单类型:</label></td>
        <td><label>选择日期:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="invoiceType"><option value="Monthly">月结单</option><option value="Daily">日结单</option></select></td>
        <td class="no-drag"><input type="date" class="input_text" id="invoiceDate" value=""></td>
    </tr>

    <tr>
        <td class="select no-drag"><select id="accType18">
            <option value="normal">普通账户</option>
            <option value="gm">GM账户</option>
            <option value="futures">期货账户</option>
            <option value="options">期权账户</option>
            </select>
        </td>
        <td class="no-drag"><button class="waves bg_color6" id="button18">点击执行</button></td>
    </tr>
</table>`},
    {"i":"9","id":"card9","t":"查询TTL账户clientID","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>输入账户:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env6"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="name6" placeholder="必填"></td>
    </tr>
    <tr>
        <td><label>输入密码:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="pword6" value="aaaa1111"></td>
        <td class="no-drag"><button id="button6" class="waves bg_color2">点击查询</button></td>
    </tr>
</table>`},
    {"i":"10","id":"card10","t":"港股串流灰度控制","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>设置尾号放量:</label></td>
        <td><label>添加白名单:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env2"><option value="test">TEST</option><option value="uat">UAT</option><option value="dev">DEV</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="end" placeholder="0~9" title="设置手机尾号放量为 0 to n(包括0与 n) n∈[0,9];
n 为 -1 时，关闭整个尾号放量规则。" value=""></td>
        <td class="no-drag"><input type="text" class="input_text" id="id_tel" placeholder="deviceId/phone" value=""></td>
    </tr>
    <tr>
        <td><label></label></td>
        <td class="no-drag"><button id="button2_3" class="waves bg_color1 m_top_5">点击设置</button></td>
        <td class="no-drag"><button id="button2_4" class="waves bg_color1 m_top_5">点击添加</button></td>
    </tr>
    <tr>
        <td><label>移除白名单:</label></td>
        <td><label>切国内外IP:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="id_tel2" placeholder="deviceId/phone" value=""></td>
        <td class="select no-drag"><select id="mockIP"><option value="all-cn">国内IP</option><option value="all-global">国外IP</option></select></td>
        <td class="no-drag"><button id="button2_1" class="waves bg_color1">查看灰度</button></td>
    </tr>
    <tr>
        <td class="no-drag"><button id="button2_5" class="waves bg_color1 m_top_5">点击移除</button></td>
        <td class="no-drag"><button id="button2_6" class="waves bg_color1 m_top_5">点击切换</button></td>
        <td class="no-drag"><button id="button2_2" class="waves bg_color1">清空白名单</button></td>
    </tr>
</table>`},
    {"i":"11","id":"card11","t":"CMS内开户","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>账户类型:</label></td>
        <td><label>证件类型:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env11"><option value="test">TEST</option><option value="uat">UAT</option><option value="dev">DEV</option></select></td>
        <td class="select no-drag"><select id="acc_type11"><option value="1">个人账户</option><option value="2">法团客户</option><option value="3">金融机构户</option></select></td>
        <td class="select no-drag">
            <select id="cardType">
                <option value="China ID">中国身份证</option>
                <option value="Hongkong ID">香港身份证</option>
                <option value="EPP">港澳通行证</option>
                <option value="Passport">中国护照</option>
            </select>
        </td>
    </tr>
    <tr>
        <td class="no-drag"><label>输入手机号:</label></td>
        <td class="no-drag"><label>输入aecode:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="tel11" value="" placeholder="为空随机生成"></td>
        <td class="no-drag"><input type="text" class="input_text" id="aecode" value="988"></td>
        <td class="no-drag"><button id="button11" class="waves bg_color2">点击开户</button></td>
    </tr>
</table>`},
    {"i":"12","id":"card12","t":"APP 开户","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>输入手机号:</label></td>
        <td><label>输入邮箱:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env14"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="tel14" value="" placeholder="为空随机生成"></td>
        <td class="no-drag"><input type="text" class="input_text" id="emai14" value="" placeholder="为空随机生成"></td>
    </tr>
    <tr>
        <td class="td_checkbox no-drag" id="tip14_1" rowspan="2">
            <label class="label-tip"><input type="checkbox" id="margin" checked="checked"><span id="margin_desc">需要孖展账户</span></label><br>
            <label class="label-tip"><input type="checkbox" id="active"><span id="active_desc">需要审核并激活</span></label><br>
            <label class="label-tip"><input type="checkbox" id="setPwd" checked="checked" disabled><span class="gray" id="setPwd_desc">需要修改账户密码</span></label>
        </td>
        <td class="td_checkbox no-drag" id="tip14_2" rowspan="2">
            <label class="label-tip"><input type="checkbox" id="setPwdTel" checked="checked" disabled><span class="gray" id="setPwdTel_desc">需要设置手机账户密码</span></label><br>
            <label class="label-tip"><input type="checkbox" id="w8" checked="checked" disabled><span class="gray" id="w8_desc">需要提交w8</span></label><br>
            <label class="label-tip"><input type="checkbox" id="market" checked="checked" disabled><span class="gray" id="market_desc">需要开通市场</span></label>
        </td>
        <td class="no-drag"><label>推荐号:</label></td>
    </tr>
    <tr><td><input type="text" class="input_text" id="invite_code" value="" placeholder="选填"></td></tr>
    <tr>
        <td class="no-drag" colspan="2"><span class="tips">Tips: 此方式为直接请求接口开户，不受前端逻辑限制。</span></td>
        <td><button id="button14" class="waves bg_color2">点击开户</button></td>
    </tr>
</table>`},
    {"i":"13","id":"card13","t":"其它","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>RPQ风险测评:</label></td>
        <td><label>解析proto数据:</label></td>
        <td><label>添加静态资产:</label></td>
        <td><label>开通市场:</label></td>
    </tr>
    <tr>
        <td class="select no-drag"><select id="env8"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td class="no-drag"><input type="text" class="input_text" id="num8" placeholder="账户号空格分割"></td>
        <td class="no-drag"><input type="text" class="input_text" id="data_pb2" value="" placeholder="输入16进制数据" title="例: 03E9 0000 0000 0001 B411 0000 0066 6E59 B834 469E 26FF 4D78 2030 E271 9252 D53C B2A4 0000 0000 0000 0000 2264 0801 1222 675F 3066 6164 6466 6134 3130 3136 3431 3338 3933 3837 3838 3238 3134 6438 3437 3539 1A2F 5F5F 7665 7274 782E 7773 2E61 3434 6533 6637 382D 3931 6266 2D34 3239 302D 6137 3636 2D38 6533 6164 3463 3230 3236 3538 FFFF FFFF FFFF FFFF FF01 4A00"></td>
        <td class="no-drag"><input type="text" class="input_text" id="name8" placeholder="账户号"></td>
        <td class="no-drag"><input type="text" class="input_text" id="name8_3" placeholder="账户号"></td>
    </tr>
    <tr>
        <td><label></label></td>
        <td class="no-drag"><button id="button8_1" class="waves bg_color4 m_top_5">点击测评</button></td>
        <td class="no-drag"><button id="button8" class="waves bg_color4 m_top_5">点击解析</button></td>
        <td class="no-drag"><button id="button8_2" class="waves bg_color4 m_top_5">点击执行</button></td>
        <td class="no-drag"><button id="button8_3" class="waves bg_color4 m_top_5">点击执行</button></td>
    </tr>
</table>`},
    {"i":"14","id":"card14","t":"UI自动化控制","ele":`
<table>
    <tr>
        <td><label>查询进程:</label></td>
        <td><label>Appium服务:</label></td>
        <td><label>WDA服务:</label></td>
        <td><label>UI自动化:</label></td>
        <td><label>终止进程:</label></td>
    </tr>
    <tr>
        <td class="no-drag"><input type="text" class="input_text" id="processName" value="" placeholder="进程名称"></td>
        <td class="select no-drag" id="appium">
            <select class="selects fappium" multiple="multiple">
                <option value="4723">4723</option>
                <option value="4725">4725</option>
                <option value="4727">4727</option>
                <option value="4729">4729</option>
                <option value="4731">4731</option>
                <option value="4733">4733</option>
            </select>
        </td>
        <td class="select no-drag" id="wda">
            <select class="selects fwda" multiple="multiple">
                <option value="8100">iPhone 11 Pro Max</option>
                <option value="8101">iPhone 11 Pro</option>
                <option value="8102">iPhone 11</option>
                <!-- <option value="13_6_ProMax">8103_13_6_ProMax</option> -->
            </select>
        </td>
        <td class="select no-drag" id="ui_auto">
            <select class="selects fui_auto" multiple="multiple">
                <option value="runTest_104.sh">runTest_104.sh</option>
                <option value="runTest_105.sh">runTest_105.sh</option>
                <option value="runTest_106.sh">runTest_106.sh</option>
                <!-- <option value="runTest_107_abc.sh">runTest_107_abc.sh</option> -->
                <option value="runTest_iOS.sh">runTest_iOS.sh</option>
                <option value="runTest_iOSp.sh">runTest_iOSp.sh</option>
                <option value="runTest_iOSpm.sh">runTest_iOSpm.sh</option>
                <!-- <option value="runTest_iOSpm_abc.sh">runTest_iOSpm_abc.sh</option> -->
                <option value="sendmail">发送邮件</option>
            </select>
        </td>
        <td class="no-drag"><input type="text" class="input_text" id="processID" value="" placeholder="进程ID,空格分隔"></td>
    </tr>
    <tr>
        <td class="no-drag"><button id="button13_1" class="waves bg_color5 m_top_5">点击查询</button></td>
        <td class="no-drag">
            <button id="button13_2_stop" class="waves bg_color5 m_top_5 width_45">停止</button>
            <button id="button13_2_start" class="waves bg_color5 m_top_5 width_45">启动</button>
        </td>
        <td class="no-drag">
            <button id="button13_3_stop" class="waves bg_color5 m_top_5 width_45">停止</button>
            <button id="button13_3_start" class="waves bg_color5 m_top_5 width_45">启动</button>
        </td>
        <td class="no-drag"><button id="button13_4" class="waves bg_color5 m_top_5">启动测试</button></td>
        <td class="no-drag"><button id="button13_5" class="waves bg_color5 m_top_5">点击终止</button></td>
    </tr>
</table>`},
    {"i":"15","id":"card15","t":"解绑证券账户","ele":`
<table>
    <tr>
        <td><label>选择环境:</label></td>
        <td><label>输入账户:</label></td>
    </tr>
    <tr>
        <td class="select"><select id="env12"><option value="test">TEST</option><option value="uat">UAT</option></select></td>
        <td><input type="text" class="input_text" id="name12" placeholder="必填"></td>
    </tr>
    <tr>
        <td><label>输入密码:</label></td>
        <td><label></label></td>
    </tr>
    <tr>
        <td><input type="text" class="input_text" id="pword12" value="aaaa1111"></td>
        <td><button id="button12" class="waves bg_color6">点击解绑</button></td>
    </tr>
</table>`},
];
var _wPX={
"0":200,"1":406,"2":200,"3":406,"4":613,"5":406,"6":200,"7":200,"8":200,"9":200,"10":406,"11":406,"12":406,"13":613,"14":613,"15":200   
};

$.ajax({
        url:'http://{0}/getViewXY'.format(host),
        data:{"width":document.body.scrollWidth*0.99},
        // dataType:'json/xml/html',
        cache:true,
        async:false,
        type:"GET",
        success:function (response){
            viewxy = response['result'];//响应结果
            for(var i in layout_func){
                // layout_func[i].x=viewxy[layout_func[i].i][0];
                // layout_func[i].y=viewxy[layout_func[i].i][1];
                layout_func[i].x=viewxy[layout_func[i].i].x;
                layout_func[i].y=viewxy[layout_func[i].i].y;
                // layout_func[i].w=viewxy[layout_func[i].i].w;
                layout_func[i].w=_wPX[i]/((document.body.scrollWidth*0.99)/24);
                layout_func[i].h=viewxy[layout_func[i].i].h;

            };
        }
    });
    return layout_func;
};

// function saveViewXY(){
//     $.ajax({
//         url:'http://10.0.2.12:8000/saveViewXY',
//         data:{"data":viewxy},
//         contentType: "application/json;charset=UTF-8",
//         cache:false,
//         // async:false,
//         type:"POST",
//         success:function (response){
//             var result=response;
//         }
//     });
//     return result
// };

var vueApp=new Vue({
    el: '#app',
    delimiters: ["{[", "]}"],
    // components: {
    //     "GridLayout": GridLayout,
    //     "GridItem": GridItem
    // },
    data: {
        layout: getLayout(),
        layout2: [{"x":0,"y":0,"w":12,"h":39,"i":"16","id":"card16","static":true,"t":"控制台","ele":``}],
        isHide: true,
        // resizable: true,
        // responsive: true,
        index: 0,
        output:''
    },
    mounted: function () {
        this.index = this.layout.length;
        this.$nextTick(function () {
            this.show = true;
            window.addEventListener('resize', () => { //监听浏览器窗口大小改变
                location.reload();//浏览器变化执行动作
              });
        })
    },
    methods: {
        out_print:function(newText,timestr=true){
            if (timestr) {
                var now_txt='['+getFormatTime()+']:';
            } else{
                var now_txt='';
            };
            var old_output=this.output;
            this.output=old_output+now_txt+newText+'\n';
        },
        ajax_req:function(path,msg,method,postData){
            this.out_print(msg);
            $.ajax({
                url:'http://{0}{1}'.format(host,path),
                data:JSON.stringify(postData),
                contentType: "application/json;charset=UTF-8",
                cache:false,
                // async:false,
                type:method,
                success: (response) => {
                    var respJson=response;
                    try {
                        if (respJson.format) {
                            this.out_print('结果:');

                            if (respJson.format=="account") {
                                this.out_print("  账户号      密码        手机号          card_ID",false);
                            }else if (respJson.format=="ttl_gary"){
                                this.out_print("            UUID                     灰度类型  状态 备注",false);
                            };

                            for (var i = respJson.result.length - 1; i >= 0; i--) {
                                this.out_print(JSON.stringify(respJson.result[i]),false);
                            };
                        }else{
                            this.out_print(JSON.stringify(respJson));
                        };
                    } catch(e) {
                        console.log('捕获到异常：',e);
                        this.out_print(respJson);
                    };
                },
                error:(XMLHttpRequest, textStatus, errorThrown)=>{
                    this.out_print("Error: {0}".format(XMLHttpRequest.status));
                    // var result = eval("("+XMLHttpRequest.responseText+")");
                    console.log(XMLHttpRequest.responseText);
                }
            });
        },
        moveEvent: function(i, newX, newY){
            console.log("moving i=" + i + ", X=" + newX + ", Y=" + newY);
            document.getElementsByClassName("vue-grid-placeholder")[0].className="vue-grid-item vue-grid-placeholder cssTransforms "+this.layout[i].id

        },
        movedEvent: function(i, newX, newY){
            this.isHide=false;
            const msg = "moved i=" + i + ", X=" + newX + ", Y=" + newY;
            console.log(msg);
            this.layout[i].x=newX;
            this.layout[i].y=newY;
            this.layout[i].w=document.getElementsByClassName("card"+i)[0].offsetWidth/(document.querySelector(".layout").offsetWidth/24);
            // console.log(this.layout);
        },
        saveViewxy(event){
            this.isHide=true;
            // this.out_print('你点击了保存按钮');
            for(var i in this.layout){
                // viewxy[this.layout[i].i]={"x":this.layout[i].x,"y":this.layout[i].y};
                viewxy[this.layout[i].i]={"x":this.layout[i].x,"y":this.layout[i].y,"w":this.layout[i].w,"h":this.layout[i].h};
            };
            this.ajax_req('/saveViewXY','保存配置','POST',{"data":viewxy,"width":document.querySelector(".layout").offsetWidth})
            // console.log(viewxy);

        },
        clearPrint(event){
            this.output='';
        },
        clickFunc(event){
            var eleID=event.target.id;
            if (event.target.nodeName==='BUTTON') {
                // console.log('你点击了 '+eleID);
                if (eleID=='button5') {
                    var env=document.getElementById("env5").value;
                    var num=document.getElementById("input5").value;
                    var msg='查询{0}环境账户 随机{1}个 开始执行...'.format(env,num);
                    var path='/getTestAccount?env={0}&num={1}'.format(env,num);
                    this.ajax_req(path,msg,'GET',null);
                } else if (eleID=='button4') {
                    var env=document.getElementById("env4").value;
                    var currency=document.querySelector('#currency .fs-label').getAttribute("value");
                    var acc=document.getElementById("name4").value;
                    var money=parseFloat(document.getElementById("money").value);
                    if (money>0){
                        var in_out='存入';
                    } else {
                        var in_out='提取';
                    };
                    if (currency.indexOf('请选择')!=-1) {currency=null};
                    if (currency && acc && money){
                        currency=currency.replaceAll(',','');
                        var path="/ttl_inMoney?env={0}&currency={1}&account={2}&money={3}&check=1".format(env,currency,acc,money);
                        var msg='{0} 环境 {1} 资金{2} {3} {4} 并审核 开始执行,请耐心等待,不要重复点击...'.format(env,acc,in_out,Math.abs(money),currency);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button9') {
                    var env=document.getElementById("env9").value;
                    var acc=document.getElementById("name9").value;
                    var markettype=document.getElementById("markettype").value;
                    var stockcode=document.getElementById("stockcode").value;
                    var stocknum=document.getElementById("stocknum").value;
                    if (acc && stockcode && stocknum){
                        var msg='{0}环境{1}加持仓 {2} 数量 {3} 开始执行...'.format(env,acc,stockcode,stocknum);
                        var path="/ttl_addHold?env={0}&account={1}&markettype={2}&stockcode={3}&stocknum={4}".format(env,acc,markettype,stockcode,stocknum);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button3') {
                    var env=document.getElementById("env3").value;
                    var acc=document.getElementById("name3").value;
                    var pwd=document.getElementById("pword3").value;
                    var resetType=document.getElementById("resetType").value;
                    if (acc && pwd) {
                        var path="/ttl_resetPwd?resetType={0}&env={1}&account={2}&pword={3}".format(resetType,env,acc,pwd);
                        var msg='{0} 环境重置 {1} 密码为 {2} 开始执行...'.format(env,acc,pwd);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                    // @bind("#resetType","mouseout")
                    // @bind("#resetType","mouseover")
                    // def change_bg_color3(event):
                    //     resetType=document["resetType"].value
                    //     if resetType=='BOSS':
                    //         document["button3"].className="waves bg_color1"
                    //         document["lineText3"].className="line_text color1"
                    //     elif resetType=='APP':
                    //         document["button3"].className="waves bg_color2"
                    //         document["lineText3"].className="line_text color2"
                    //     elif resetType=='CGF':
                    //         document["button3"].className="waves bg_color3"
                    //         document["lineText3"].className="line_text color3"
                } else if (eleID=='button6') {
                    var env=document.getElementById("env6").value;
                    var acc=document.getElementById("name6").value;
                    var pwd=document.getElementById("pword6").value;
                    if (acc && pwd) {
                        var path="/queryTTLclientId?env={0}&account={1}&pword={2}".format(env,acc,pwd);
                        var msg='查询TTL-{0}环境 {1} 对应clientID'.format(env,acc);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button7') {
                    var env=document.getElementById("env7").value;
                    var acc=document.getElementById("name7").value;
                    if (acc) {
                        var path="/unlockAccount?env={0}&account={1}".format(env,acc);
                        var msg='解锁 {0} 环境账户 {1}'.format(env,acc);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button2_1') {
                    var env=document.getElementById("env2").value;
                    var path="/grayControl?method=get&env={0}".format(env);
                    var msg='查询{0}环境灰度设置'.format(env);
                    this.ajax_req(path,msg,'GET',null);

                } else if (eleID=='button2_2') {
                    var result=confirm('确 定 ？');
                    if (result) {
                        var env=document.getElementById("env2").value;
                        var path="/grayControl?method=delAll&env={0}".format(env);
                        var msg='清空{0}环境所有白名单'.format(env);
                        this.ajax_req(path,msg,'GET',null);
                    };
                } else if (eleID=='button2_3') {
                    var env=document.getElementById("env2").value;
                    var kword=document.getElementById("end").value;
                    if (kword) {
                        var path="/grayControl?method=edit&env={0}&kword={1}".format(env,kword);
                        var msg='修改{0}环境灰度尾号放量为 0-{1}'.format(env,kword);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button2_4') {
                    var env=document.getElementById("env2").value;
                    var kword=document.getElementById("id_tel").value;
                    if (kword) {
                        var path="/grayControl?method=add&env={0}&kword={1}".format(env,kword);
                        var msg='添加{0}环境灰度白名单 {1}'.format(env,kword);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button2_5') {
                    var env=document.getElementById("env2").value;
                    var kword=document.getElementById("id_tel2").value;
                    if (kword) {
                        var path="/grayControl?method=del&env={0}&kword={1}".format(env,kword);
                        var msg='删除{0}环境灰度白名单 {1}'.format(env,kword);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button2_6') {
                    var env=document.getElementById("env2").value;
                    var ip=document.getElementById("mockIP").value;
                    var path="/grayControl?method=mockIP&env={0}&kword={1}".format(env,ip);
                    var msg='切换{0}环境mockIP为{1}'.format(env,ip);
                    this.ajax_req(path,msg,'GET',null);
                } else if (eleID=='button11') {
                    var env=document.getElementById("env11").value;
                    var tel=document.getElementById("tel11").value;
                    var email='';
                    var aecode=document.getElementById("aecode").value;

                    var select=document.getElementById("acc_type11");
                    var accTypeText=select.options[select.selectedIndex].text;
                    var accType=select.value;

                    var cardType=document.getElementById("cardType").value;
                    var path="/cms_createUesr?env={0}&accType={1}&tel={2}&email={3}&aecode={4}&cardType={5}".format(env,accType,tel,email,aecode,cardType);
                    var msg='{0}环境CMS内开 {1} 开始执行...'.format(env,accTypeText);
                    this.ajax_req(path,msg,'GET',null);
                } else if (eleID=='button12') {
                    var env=document.getElementById("env12").value;
                    var acc=document.getElementById("name12").value;
                    var pwd=document.getElementById("pword12").value;

                    if (acc) {
                        var path="/unBinding?env={0}&account={1}&pword={2}".format(env,acc,pwd);
                        var msg='{0} 环境 {1} 解绑证券账户 开始执行...'.format(env,acc);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_1') {
                    var processName=document.getElementById("processName").value;
                    if (processName) {
                        var path="/UIAutoControl?server=query&processName={0}".format(processName);
                        var msg='查询进程 {0} 开始执行...'.format(processName);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_2_stop') {
                    var appiumPort=document.querySelector('#appium .fs-label').getAttribute("value").replaceAll(',',' ');
                    if (appiumPort) {
                        var path="/UIAutoControl?server=appium&method=stop&appiumPort={0}".format(appiumPort);
                        var msg='停止appium {0} 开始执行...'.format(appiumPort);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_2_start') {
                    var appiumPort=document.querySelector('#appium .fs-label').getAttribute("value").replaceAll(',',' ');
                    if (appiumPort) {
                        var path="/UIAutoControl?server=appium&method=start&appiumPort={0}".format(appiumPort);
                        var msg='启动appium {0} 开始执行...'.format(appiumPort);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_3_stop') {
                    var iosNames=document.querySelector('#wda .fs-label').getAttribute("value").split(',');
                    var wdaPort='';
                    if (iosNames) {
                        for (var i = iosNames.length - 1; i >= 0; i--) {
                            var iosName=iosNames[i].replace(/(^\s*)|(\s*$)/g, "");
                            if ('iPhone 11 Pro Max'==iosName) {
                                wdaPort+='8100 ';
                            } else if ('iPhone 11 Pro'==iosName) {
                                wdaPort+='8101 ';
                            } else if ('iPhone 11'==iosName) {
                                wdaPort+='8102 ';
                            };
                        };
                        var path="/UIAutoControl?server=wda&method=stop&wdaPort={0}".format(wdaPort);
                        var msg='停止wda {0} 开始执行...'.format(wdaPort);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_3_start') {
                    var iosNames=document.querySelector('#wda .fs-label').getAttribute("value").split(',');
                    var wdaPort='';
                    if (iosNames){
                        for (var i = iosNames.length - 1; i >= 0; i--) {
                            var iosName=iosNames[i].replace(/(^\s*)|(\s*$)/g, "");
                            if ('iPhone 11 Pro Max'==iosName) {
                                wdaPort+='8100 ';
                            } else if ('iPhone 11 Pro'==iosName) {
                                wdaPort+='8101 ';
                            } else if ('iPhone 11'==iosName) {
                                wdaPort+='8102 ';
                            };
                        };
                        var path="/UIAutoControl?server=wda&method=start&wdaPort={0}".format(wdaPort);
                        var msg='启动wda {0} 开始执行...'.format(wdaPort);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_4') {
                    var shellName=document.querySelector('#ui_auto .fs-label').getAttribute("value").replaceAll(',',' ');
                    if (shellName) {
                        var path="/UIAutoControl?server=startUI&shellName={0}".format(shellName);
                        var msg='启动UI自动化测试 {0} 开始执行...'.format(shellName);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button13_5') {
                    var processID=document.getElementById("processID").value;
                    if (processID) {
                        var path="/UIAutoControl?server=killProcessID&processID={0}".format(processID);
                        var msg='终止进程 {0} 开始执行...'.format(processID);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button14') {
                    var env=document.getElementById("env14").value;
                    var tel=document.getElementById("tel14").value;
                    var email=document.getElementById("emai14").value;
                    var invite_code=document.getElementById("invite_code").value;
                    var margin=Number(document.getElementById("margin").checked);
                    var active=Number(document.getElementById("active").checked);
                    var setPwd=Number(document.getElementById("setPwd").checked && (!document.getElementById("setPwd").disabled));
                    var setPwdTel=Number(document.getElementById("setPwdTel").checked && (!document.getElementById("setPwdTel").disabled));
                    var w8=Number(document.getElementById("w8").checked && (!document.getElementById("w8").disabled));
                    var market=Number(document.getElementById("market").checked && (!document.getElementById("market").disabled));
                    var path="/regByApi?env={0}&acc_type=TTL&tel={1}&email={2}&margin={3}&active={4}&setPwd={5}&setPwdTel={6}&w8={7}&market={8}&invite_code={9}".format(env,tel,email,margin,active,setPwd,setPwdTel,w8,market,invite_code);
                    var msg=' {0}环境 app开户 开始执行...'.format(env);
                    this.ajax_req(path,msg,'GET',null);
                } else if (eleID=='button15') {
                    var env=document.getElementById("env15").value;
                    var bankName=document.getElementById("bankName").value;
                    var currency=document.querySelector('#currency15 .fs-label').getAttribute("value");
                    var acc=document.getElementById("name15").value;
                    var bankNum=document.getElementById("bankNum").value;
                    var money=document.getElementById("money15").value;
                    var tradeDate=document.getElementById("tradeDate").value.replaceAll('-','').replaceAll('/','').replaceAll(' ','');
                    var auto_bankReg=Number(document.getElementById("bankReg").checked);
                    var auto_addBank=Number(document.getElementById("addBank").checked);
                    if (currency.indexOf('请选择')!=-1) {currency=null};
                    if (currency && acc && money && bankNum && tradeDate){
                        currency=currency.replaceAll(',','');
                        var path="/bankSecuritiesAddMoney?env={0}&account={1}&bankName={2}&bankNum={3}&currency={4}&money={5}&tradeDate={6}&auto_bankReg={7}&auto_addBank={8}".format(env,acc,bankName,bankNum,currency,money,tradeDate,auto_bankReg,auto_addBank);
                        var msg='{0} 环境 {1} {2}银证入金 {3} {4} 开始执行,请耐心等待,不要重复点击...'.format(env,acc,bankName,currency,money);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                
                } else if (eleID=='button16') {
                    var env=document.getElementById("env16").value;
                    var newStockname=document.getElementById("newStockname").value;
                    var newStockcode=document.getElementById("newStockcode").value;
                    var path="/addIPO?env={0}&stockname={1}&stockcode={2}".format(env,newStockname,newStockcode);
                    var msg='{0} 环境创建新股开始执行'.format(env);
                    this.ajax_req(path,msg,'GET',null);
                } else if (eleID=='button17') {
                    var env=document.getElementById("env17").value;
                    var account=document.getElementById("name17").value;
                    var sessionid=document.getElementById("sessionid").value;
                    if (account && sessionid){
                        var path="/accountLogout?env={0}&account={1}&sessionid={2}".format(env,account,sessionid);
                        var msg='{0} 环境 {1} session失效 开始执行'.format(env,account);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button8') {
                    var data=document.getElementById("data_pb2").value;
                    if (data){
                        var path="/parsePB2";
                        var msg='解析protocol数据...';
                        this.ajax_req(path,msg,'POST',{"data":data});
                    } else { 
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button8_1') {
                    var env8=document.getElementById("env8").value;
                    var num8=document.getElementById("num8").value;
                    if (num8) {
                        // var path="/getKafkalog?env={0}&num={1}".format(env8,num8);
                        // var msg='查询{0}环境Kafka日志最近 {1} 条...'.format(env8,num8);
                        var path="/rpqTest?env={0}&accounts={1}".format(env8,num8);
                        var msg='{0}环境 {1} RPQ风险测评...'.format(env8,num8);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button8_2') {
                    var env=document.getElementById("env8").value;
                    var account=document.getElementById("name8").value;
                    if (account) {
                        var path="/portfolio?env={0}&account={1}".format(env,account);
                        var msg='{0} 环境{1} 添加静态资产 开始执行'.format(env,account);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button8_3') {
                    var env=document.getElementById("env8").value;
                    var account=document.getElementById("name8_3").value;
                    if (account) {
                        var path="/openmarket?env={0}&account={1}".format(env,account);
                        var msg='{0} 环境{1} 开通市场 开始执行'.format(env,account);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='button18') {
                    var env=document.getElementById("env18").value;
                    var acc=document.getElementById("name18").value;
                    var accType18=document.getElementById("accType18").value;
                    var invoiceType=document.getElementById("invoiceType").value;
                    var invoiceDate=document.getElementById("invoiceDate").value.replaceAll('/','-');
                    if (acc && invoiceDate) {
                        var path="/uploadPDF?env={0}&account={1}&invoiceType={2}&invoiceDate={3}&accType={4}".format(env,acc,invoiceType,invoiceDate,accType18);
                        var msg='{0} 环境 {1} 推送结单文件 开始执行...'.format(env,acc);
                        this.ajax_req(path,msg,'GET',null);
                    } else {
                        this.out_print('无效操作。缺少参数，请检查。');
                    };
                } else if (eleID=='selectAllBtn') {
                    console.log('你点击了全选按钮');
                } else if (eleID=='clearAllBtn') {
                    console.log('你点击了清空按钮');
                } else {
                    this.out_print('功能仍在完善中');
                };                
            } else if (event.target.nodeName==='INPUT') {
                if (eleID=='active') {
                    var active=document.getElementById("active");
                    var setPwd=document.getElementById("setPwd");
                    if (active.checked){
                        document.getElementById("setPwd").disabled=false;
                        document.getElementById("setPwd_desc").className="";
                        if (setPwd.checked) {
                            document.getElementById("setPwdTel").disabled=false;
                            document.getElementById("setPwdTel_desc").className="";
                            document.getElementById("w8").disabled=false;
                            document.getElementById("w8_desc").className="";
                            document.getElementById("market").disabled=false;
                            document.getElementById("market_desc").className="";
                        } else {
                            document.getElementById("setPwdTel").disabled=true;
                            document.getElementById("setPwdTel_desc").className="gray";
                            document.getElementById("w8").disabled=true;
                            document.getElementById("w8_desc").className="gray";
                            document.getElementById("market").disabled=true;
                            document.getElementById("market_desc").className="gray";
                        };
                    } else {
                        document.getElementById("setPwd").disabled=true;
                        document.getElementById("setPwd_desc").className="gray";

                        document.getElementById("setPwdTel").disabled=true;
                        document.getElementById("setPwdTel_desc").className="gray";
                        document.getElementById("w8").disabled=true;
                        document.getElementById("w8_desc").className="gray";
                        document.getElementById("market").disabled=true;
                        document.getElementById("market_desc").className="gray";
                    };
                } else if (eleID=='setPwd') {
                    var setPwd=document.getElementById("setPwd");
                    if (setPwd.checked){
                        document.getElementById("setPwdTel").disabled=false;
                        document.getElementById("w8").disabled=false;
                        document.getElementById("market").disabled=false;
                        document.getElementById("setPwdTel_desc").className="";
                        document.getElementById("w8_desc").className="";
                        document.getElementById("market_desc").className="";
                    } else {
                        document.getElementById("setPwdTel").disabled=true;
                        document.getElementById("w8").disabled=true;
                        document.getElementById("market").disabled=true;
                        document.getElementById("setPwdTel_desc").className="gray";
                        document.getElementById("w8_desc").className="gray";
                        document.getElementById("market_desc").className="gray";
                    };
                } else if (eleID=='bankReg') {
                    var bankReg=document.getElementById("bankReg");
                    if (bankReg.checked) {
                        document.getElementById("addBank").disabled=false;
                        document.getElementById("addBank_desc").className="";
                    } else {
                        document.getElementById("addBank").disabled=true;
                        document.getElementById("addBank_desc").className="gray";
                    };
                };
            } else {
                console.log(event.target.nodeName);
            };
        }



    }

});

/*
function generateLayout() {
    return _.map(_.range(0, 25), function (item, i) {
        var y = Math.ceil(Math.random() * 4) + 1;
        return {
            x: _.random(0, 5) * 2 % 12,
            y: Math.floor(i / 6) * y,
            w: 2,
            h: y,
            i: i.toString(),
            static: Math.random() < 0.05
        };
    });
}*/



