{* Smarty *}
<html>
<head>
<meta http-equiv='content' content='text/html;charset=utf-8'/>
<link rel='stylesheet' type='text/css' href='{$web_prefix}/css/main.css'/>
<script language='JavaScript' src='{$web_prefix}/js/main.js'></script>
</head>
<body>
{include file='header.tpl'}
<div id='content'>
    <p><a href="?">&lt;&lt;&nbsp;назад</a></p>
    <h2>Группы граммем</h2>
    {if $is_admin}
    <b>Добавить группу</b>:
    <form action="?act=add_gg" method="post" class="inline">
        <input name="g_name" value="&lt;Название&gt;">
        <input type="submit" value="Добавить"/>
    </form>
    <br/><br/>
    <b>Добавить граммему</b>:<br/>
    <form action="?act=add_gram" method="post" class="inline">
        Внутр. ID <input name="g_name" value="grm" size="10" maxlength="20"/>,
        внешн. ID <input name="aot_id" value="грм" size="10" maxlength="20"/>,
        группа <select name="group">{$editor.select}</select>,<br/>
        описание <input name="descr" size="40"/>
        <input type="submit" value="Добавить"/>
    </form>
    <br/><br/>
    {/if}
    <form action="?act=edit_gram" method="post">
    <table border="1" cellspacing="0" cellpadding="2">
        <tr><th>Внутр. ID<th>Внешн. ID<th>Описание{if $is_admin}<th>&nbsp;{/if}</tr>
        {foreach key=id item=group from=$editor.groups}
            <tr><td colspan="2"><b>{$group.name}</b><td>&nbsp;{if $is_admin}<td>[<a href='?act=move_gg&dir=up&id={$id}'>вверх</a>] [<a href='?act=move_gg&dir=down&id={$id}'>вниз</a>]{else}&nbsp;{/if}</tr>
            {foreach item=grammem from=$group.grammems}
                <tr><td>{$grammem.name}<td>{$grammem.aot_id|default:'&nbsp;'}<td>{$grammem.description}{if $is_admin}<td>[<a href='?act=move_gram&dir=up&id={$grammem.id}'>вверх</a>] [<a href='?act=move_gram&dir=down&id={$grammem.id}'>вниз</a>] [<a href='#' onClick='edit_gram(this, {$grammem.id}); return false;'>ред.</a>]{else}&nbsp;{/if}</tr>
            {/foreach}
        {/foreach}
    </table>
    </form>
</div>
<div id='rightcol'>
{include file='right.tpl'}
</div>
</body>
</html>
