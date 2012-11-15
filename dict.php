<?php
require('lib/header.php');
require('lib/lib_dict.php');
if (isset($_GET['act']))
    $action = $_GET['act'];
else $action = '';

$smarty->assign('active_page','dict');

//check permissions
if (!in_array($action, array('', 'gram', 'gram_restr', 'lemmata', 'errata', 'edit')) &&
    !user_has_permission('perm_dict')) {
        show_error($config['msg']['notadmin']);
        return;
}

switch ($action) {
    case 'add_gram':
        $name = mysql_real_escape_string($_POST['g_name']);
        $group = (int)$_POST['parent_gram'];
        $outer_id = mysql_real_escape_string($_POST['outer_id']);
        $descr = mysql_real_escape_string($_POST['descr']);
        if (add_grammem($name, $group, $outer_id, $descr))
            header("Location:dict.php?act=gram");
        else
            show_error();
        break;
    case 'move_gram':
        $grm = (int)$_GET['id'];
        $dir = $_GET['dir'];
        if (move_grammem($grm, $dir))
            header('Location:dict.php?act=gram#g'.$grm_id);
        else
            show_error();
        break;
    case 'del_gram':
        if (del_grammem((int)$_GET['id']))
            header("Location:dict.php?act=gram");
        else
            show_error();
        break;
    case 'edit_gram':
        $id = (int)$_POST['id'];
        $inner_id = mysql_real_escape_string($_POST['inner_id']);
        $outer_id = mysql_real_escape_string($_POST['outer_id']);
        $descr = mysql_real_escape_string($_POST['descr']);
        if (edit_grammem($id, $inner_id, $outer_id, $descr))
            header('Location:dict.php?act=gram');
        else
            show_error();
        break;
    case 'clear_errata':
        if (clear_dict_errata(isset($_GET['old'])))
            header("Location:dict.php?act=errata");
        else
            show_error();
        break;
    case 'not_error':
        if (mark_dict_error_ok((int)$_GET['error_id'], $_POST['comm']))
            header("Location:dict.php?act=errata");
        else
            show_error();
        break;
    case 'add_restr':
        if (add_dict_restriction($_POST))
            header("Location:dict.php?act=gram_restr");
        else
            show_error();
        break;
    case 'del_restr':
        if (del_dict_restriction((int)$_GET['id']))
            header("Location:dict.php?act=gram_restr");
        else
            show_error();
        break;
    case 'update_restr':
        if (calculate_gram_restrictions())
            header("Location:dict.php?act=gram_restr");
        else
            show_error();
        break;
    case 'save':
        if ($lemma_id = dict_save($_POST))
            header("Location:dict.php?act=edit&saved&id=$lemma_id");
        else
            show_error();
        break;
    case 'add_link':
        if (add_link((int)$_POST['from_id'], (int)$_POST['lemma_id'], (int)$_POST['link_type'])) {
            header("Location:dict.php?act=edit&id=".(int)$_POST['from_id']);
        } else
            show_error();
        break;
    case 'del_link':
        if (del_link((int)$_GET['id'])) {
            header("Location:dict.php?act=edit&id=".(int)$_GET['lemma_id']);
        } else
            show_error();
        break;
    case 'del_lemma':
        if (del_lemma((int)$_GET['lemma_id']))
            header("Location:dict.php");
        else
            show_error();
        break;
    case 'lemmata':
        $smarty->assign('search', get_dict_search_results($_POST));
        $smarty->display('dict/lemmata.tpl');
        break;
    case 'gram':
        $order = isset($_GET['order']) ? $_GET['order'] : '';
        $smarty->assign('grammems', get_grammem_editor($order));
        $smarty->assign('order', $order);
        $smarty->assign('select', dict_get_select_gram());
        $smarty->display('dict/gram.tpl');
        break;
    case 'gram_restr':
        $smarty->assign('restrictions', get_gram_restrictions(isset($_GET['hide_auto'])));
        $smarty->display('dict/restrictions.tpl');
        break;
    case 'edit':
        $lid = (int)$_GET['id'];
        $smarty->assign('editor', get_lemma_editor($lid));
        $smarty->assign('link_types', get_link_types());
        $smarty->display('dict/lemma_edit.tpl');
        break;
    case 'errata':
        $smarty->assign('errata', get_dict_errata(isset($_GET['all']), isset($_GET['rand'])));
        $smarty->display('dict/errata.tpl');
        break;
    case 'pending':
        if (isset($_POST['count']))
            $count = (int)$_POST['count'];
        else
            $count = 200;
        $smarty->assign('data', get_pending_updates($count));
        $smarty->display('dict/pending.tpl');
        break;
    case 'reannot':
        if (update_pending_tokens((int)$_POST['rev_id']))
            header("Location:dict.php?act=pending");
        else
            show_error();
        break;
    default:
        $smarty->setCaching(Smarty::CACHING_LIFETIME_SAVED);
        $smarty->setCacheLifetime(600);
        if (!is_cached('dict/main.tpl', user_has_permission('perm_dict'))) {
            $smarty->assign('stats', get_dict_stats());
            $smarty->assign('dl', get_downloads_info());
        }
        $smarty->display('dict/main.tpl', user_has_permission('perm_dict'));
}
?>
