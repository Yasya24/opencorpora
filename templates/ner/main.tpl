{* Smarty *}
{extends file='common.tpl'}
{block name=content}
<div class="clearfix">
    <div class="pull-right">
        <a class="btn btn-primary" href="?act=manual" target="_blank"><i class="icon-info-sign icon-white"></i> Инструкция</a>
    </div>
</div>
<h3>Разметка именованных сущностей</h3>
<table class='table'>
<tr class='small'>
    <th></th>
    <th></th>
    <th>Абзацев</th>
    <th>Готовность</th>
    <th></th>
</tr>
{foreach from=$page item=book}
<tr {if $book.started}class='bggreen'{/if}>
    <td><a href="{$web_prefix}/books.php?book_id={$book.id}">{$book.id}</a></td>
    <td>{$book.name|htmlspecialchars}</td>
    <td>{$book.num_par}</td>
    <td>{(100 * $book.ready_annot / ($book.num_par * $smarty.const.NE_ANNOTATORS_PER_TEXT))|string_format:"%d"} %</td>
    <td>
        {if $book.available}
            <a href="{$web_prefix}/books.php?book_id={$book.id}&amp;act=ner" class="btn btn-small">Размечать</a>
        {else}
            <a href="{$web_prefix}/books.php?book_id={$book.id}&amp;act=ner" class="btn btn-small"><i class="icon-ok"></i> Просмотреть</a>
        {/if}
    </td>
</tr>
{/foreach}
</table>
{/block}
