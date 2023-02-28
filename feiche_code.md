<!--
 * @Author       : BNDou
 * @Date         : 2023-01-26 22:12:51
 * @LastEditTime : 2023-03-01 00:26:58
 * @FilePath     : /Auto_Check_In/feiche_code.md
 * @Description  :
-->

# 飞车快捷指令

## 说明

游戏里面小号给大号发邮件，复制下面所需的代码

光标移到内容上，然后 ctrl c 一直按着不放，然后点发送

大号查看邮件，发现收到的是超链接，点击即可运行

> 秒开道具（可自行设置数量 注意这个 0 点前！！提前点击一次！！会弹出空白窗口，关闭即可，然后等 0 点 点击超链接即可 1 秒开 30 个）

```
/<customlink=cmd_showTreasureBox(17455); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开金丝篓30个

/<customlink=cmd_showTreasureBox(19019); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开大青虫30个

/<customlink=cmd_showTreasureBox(16318); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开黑美人西瓜30个

/<customlink=cmd_showTreasureBox(16340); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开紫砂西瓜30个

/<customlink=cmd_showTreasureBox(19020); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开小青虫30个

/<customlink=cmd_showTreasureBox(16336); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开玉石卷轴30个

/<customlink=cmd_showTreasureBox(19396); for i = 30, 1, -1 do UI.children.AffirmMsgBox.children.comfirmButton.OnClick() end>秒开草莓30个
```

> 秒开道具（无需提前点击 时间到了点击即可）

```
/<customlink=for i = 30, 1, -1 do cmd_OpenTreasureBox(82762) end;>秒开亲密宝箱30个

/<customlink=for i = 30, 1, -1 do cmd_OpenTreasureBox(25858) end;>秒开幸运星宝瓶30个

/<customlink=for i = 30, 1, -1 do cmd_OpenTreasureBox(70910) end;>秒开宝宝狂欢礼盒30个

/<customlink=for i = 30, 1, -1 do cmd_OpenTreasureBox(70909) end;>秒开宝宝开心礼盒30个

/<customlink=for i = 30, 1, -1 do cmd_OpenTreasureBox(70906) end;>秒开爱心礼盒30个
```

> 卡游戏背景（重新登录飞车后依旧有效，点击即可切换）

```
/<customlink=ReqChangeLobbyBackGround(66)>稀世·仙履奇缘
/<customlink=ReqChangeLobbyBackGround(67)>稀世·明日之诗
/<customlink=ReqChangeLobbyBackGround(76)>稀世·创世死神
/<customlink=ReqChangeLobbyBackGround(77)>稀世·创世之神
/<customlink=ReqChangeLobbyBackGround(79)>稀世·墨龙
/<customlink=ReqChangeLobbyBackGround(85)>稀世·梁祝化蝶
/<customlink=ReqChangeLobbyBackGround(47)>稀世·鸿运锦鲤
/<customlink=ReqChangeLobbyBackGround(51)>稀世·水龙吟
/<customlink=ReqChangeLobbyBackGround(54)>稀世·星辰之语
/<customlink=ReqChangeLobbyBackGround(60)>稀世·至尊
```

> 飞车已下架模式（实际隐藏了 可获得点券百宝箱）

```
/<customlink=cmd_EnterMapDIY() >赛车随心造模式
```

---

[![](https://komarev.com/ghpvc/?username=BNDou&&label=Views "To Github")](https://github.com/BNDou/)
