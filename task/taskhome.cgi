#!/usr/bin/perl
use cPanelUserConfig;
use strict;
use warnings;


use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Usercheck);
use htmlManager qw(:elements);
use general qw(:get);
use itemDatabase qw(:Display :Item :Itemtag :Itemuser :Note :Groupitems :ItemToItem);

my $cgi = CGI->new;
my $sid = $cgi->cookie('CGISESSID') || $cgi->param('CGISESSID') || undef;
my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});

my $userrights = 0;
my $userid = "";
my $userfirstname = "";
my $userlastname = "";
my $useremail = "";
my $userclientid = "";
if ($session->param("userid"))
{
	$userid = $session->param("userid");
	$userfirstname = $session->param("userfirstname");
	$userlastname = $session->param("userlastname");
	$useremail = $session->param("useremail");
	$userclientid = $session->param("userclientid");
	$userrights = $session->param("userrights");
}else
{
	print $cgi->redirect(-url=>'http://www.c2c-hit.net/c2cmobile/login.cgi');			
}

#initial values
my $message = "";
my $query;
my $itemlist;
my $hold;# = getAnySort(["SELECT * FROM itemuserquery WHERE userid = $userid", 0, 0, 0]);
my $listtype = $cgi->param('listtype');

#UPDATE VARS
my %options;
my %selected;
my $first = 1;
my $firsti = 1;
my $id;
my $update = $cgi->param('update');
my @updatesplit;
my $idlist;
my %params;
my @paramnames;
my $info;
my $tquery;
my $count;
if ($update)
{
    @paramnames = $cgi->param;
    $query = $cgi->param('myquery');
    foreach my $paramname (@paramnames)
    {
	@{$params{$paramname}} = $cgi->param($paramname);
    }
    @updatesplit = split / /, $update;
    if ($updatesplit[1] ne 'All')
    {
	$idlist = [$updatesplit[1]];
    }else
    {
	$hold = getAnySort([$query, 0, 0, 0]);
	$count = 0;
	foreach my $item (@{$hold->[0]})
	{
	    $idlist->[$count] = $item->{'itemid'};
	    $count += 1;
	}
    }

    foreach $id (@{$idlist})
    {
	undef $info;
	#
	#----------------GEN INFO---------------------
	#
	$info->[0] = $userid;
	$info->[1] = $id;
	#
	#----------------CLIENT UPDATE
	#
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND clientid = " . $params{"$id.client"}[0], 0, 0, 0]);

	if (!$hold->[0])
	{
	    $info->[2]{'clientid'} = $params{"$id.client"}[0];
	}
	#
	#----------------NAME UPDATE
	#
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND name = '" . $params{"$id.name"}[0] . "'", 0, 0, 0]);

	if (!$hold->[0])
	{
	    $info->[2]{'name'} = $params{"$id.name"}[0];
	}

	#
	#----------------DESCRIPTION UPDATE
	#
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND description = '" . $params{"$id.description"}[0] . "'", 0, 0, 0]);

	if (!$hold->[0])
	{
	    $info->[2]{'description'} = $params{"$id.description"}[0];
	}

	#
	#----------------STATUS UPDATE
	#
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND statusid = " . $params{"$id.status"}[0], 0, 0, 0]);

	if (!$hold->[0])
	{
	    $info->[2]{'statusid'} = $params{"$id.status"}[0];
	}

	#
	#----------------STARTDATE UPDATE
	#
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND YEAR(startdate) = " . $params{"year$id.startdate"}[0] . " AND MONTH(startdate) = " . $params{"month$id.startdate"}[0] . " AND DAY(startdate) = " . $params{"day$id.startdate"}[0] . " AND HOUR(startdate) = " . $params{"hour$id.startdate"}[0] . " AND MINUTE(startdate) = " . $params{"min$id.startdate"}[0], 0, 0, 0]);

	if (!$hold->[0])
	{
	    $info->[2]{'startdate'} = $params{"year$id.startdate"}[0] . "-" . $params{"month$id.startdate"}[0] . "-" .$params{"day$id.startdate"}[0] . " " .  $params{"hour$id.startdate"}[0] . ":" . $params{"min$id.startdate"}[0] . ":" . "00";
	}

	#
	#----------------ENDDATE UPDATE
	#
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND YEAR(enddate) = " . $params{"year$id.enddate"}[0] . " AND MONTH(enddate) = " . $params{"month$id.enddate"}[0] . " AND DAY(enddate) = " . $params{"day$id.enddate"}[0] . " AND HOUR(enddate) = " . $params{"hour$id.enddate"}[0] . " AND MINUTE(enddate) = " . $params{"min$id.enddate"}[0], 0, 0, 0]);

	if (!$hold->[0])
	{
	    $info->[2]{'enddate'} = $params{"year$id.enddate"}[0] . "-" . $params{"month$id.enddate"}[0] . "-" .$params{"day$id.enddate"}[0] . " " . $params{"hour$id.enddate"}[0] . ":" . $params{"min$id.enddate"}[0] . ":" . "00";
	}
	#
	#-----------------UPDATE GEN INFO
	#

	if ($info->[2])
	{
	    $hold = addEditItem($info);
	}
	
    	#
	#----------------TAG UPDATE
	#
	##____REMOVE TAGS
	undef $info;
	$tquery = "SELECT * FROM itemtotag itt WHERE EXISTS (SELECT * FROM itemtag it WHERE it.id = itt.tagid AND it.tagdefault = 0) AND itt.itemid = $id AND itt.tagid NOT IN (";
	$first = 1;
	foreach my $tag (@{$params{"$id.tag"}})
	{
	    if ($first)
	    {
		$tquery .= "$tag";
		$first = 0;
	    }else
	    {
		$tquery .= ", $tag";
	    }
	}
	$tquery .= ")";
	$hold = getAnySort([$tquery, 0, 0, 0]);
	if ($hold->[0])
	{	    
	    $info->[0] = $id;
	    $info->[2] = $userid;
	    $count = 0;
	    foreach my $tag (@{$hold->[0]})
	    {		
		$info->[1][$count] = $tag->{'tagid'};	
		$count += 1;
	    }
	    $hold = deleteItemTags($info);
	}
	##______ADD TAGS
	undef $info;
	$tquery = "SELECT * FROM (";
	$first = 1;
	foreach my $tag (@{$params{"$id.tag"}})
	{
	    if ($first)
	    {
		$tquery .= "SELECT $tag as 'tagid' ";
		$first = 0;
	    }else
	    {
		$tquery .= "UNION SELECT $tag as 'tagid' ";
	    }
	}	
	$tquery .= ") a WHERE NOT EXISTS (SELECT * FROM itemtotag itt WHERE itt.itemid = $id AND itt.tagid = a.tagid AND EXISTS (SELECT * FROM itemtag it WHERE it.id = itt.tagid AND it.tagdefault = 0))";
	$hold = getAnySort([$tquery, 0, 0, 0]);
	if ($hold->[0])
	{	    
	    $info->[0] = $id;
	    $info->[2] = $userid;
	    $count = 0;
	    foreach my $tag (@{$hold->[0]})
	    {		
		$info->[1][$count] = $tag->{'tagid'};
		$count += 1;
	    }
	    $hold = addItemTags($info);
	}
	#
	#----------------USER UPDATE
	#
	##____REMOVE USER
	undef $info;
	$tquery = "SELECT * FROM itemtouser itu WHERE itu.itemid = $id AND itu.userid NOT IN (";
	$first = 1;
	foreach my $tag (@{$params{"$id.user"}})
	{
	    if ($first)
	    {
		$tquery .= "$tag";
		$first = 0;
	    }else
	    {
		$tquery .= ", $tag";
	    }
	}
	$tquery .= ")";
	$hold = getAnySort([$tquery, 0, 0, 0]);
	if ($hold->[0])
	{	    
	    $info->[0] = $id;
	    $info->[2] = $userid;
	    $count = 0;
	    foreach my $tag (@{$hold->[0]})
	    {		
		$info->[1][$count] = $tag->{'userid'};
		$count += 1;
	    }
	    $hold = deleteItemUser($info);
	}
	##______ADD USER
	undef $info;
	$tquery = "SELECT * FROM (";
	$first = 1;
	foreach my $tag (@{$params{"$id.user"}})
	{
	    if ($first)
	    {
		$tquery .= "SELECT $tag as 'userid' ";
		$first = 0;
	    }else
	    {
		$tquery .= "UNION SELECT $tag as 'userid' ";
	    }
	}	
	$tquery .= ") a WHERE NOT EXISTS (SELECT * FROM itemtouser itu WHERE itu.itemid = $id AND itu.userid = a.userid )";
	$hold = getAnySort([$tquery, 0, 0, 0]);
	if ($hold->[0])
	{	   
	    $info->[0] = $id;
	    $info->[2] = $userid;
	    $count = 0;
	    foreach my $tag (@{$hold->[0]})
	    {		
		$info->[1][$count] = $tag->{'userid'};
	        $count += 1;
	    }
	    $hold = addItemUser($info);
	}
	#
	#----------------NOTE UPDATE
	#
	if ($params{"$id.note"}[0])
	{
	    logLastEdit($id, $params{"$id.note"}[0], $userid, 0);
	}

    }   

}

$hold = getAnySort(["SELECT * FROM itemuserquery WHERE userid = $userid", 0, 0, 0]);
$query = $hold->[0][0]{'query'};
$message = $query;
$itemlist = getAnySort([$query, 0, 0, 0]);





#test form values and untaint

#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Task Home", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

print "<div data-role=\"controlgroup\" data-type=\"horizontal\">\n";
print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/additem.cgi\" target=\"_blank\"class=\"ui-btn ui-corner-all\">Add New</a>\n";
if ($userrights > 1)
{
    print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/addmanyitems.cgi\" target=\"_blank\"class=\"ui-btn ui-corner-all\">Add Many New</a>\n";
}
print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/itemsearch.cgi\" target=\"_blank\" class=\"ui-btn ui-corner-all\">Search</a>\n";
print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/itempreference.cgi\" target=\"_blank\" class=\"ui-btn ui-corner-all\">Set Preferences</a>\n";
if ($userrights > 1)
{
print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/editstatus.cgi\" target=\"_blank\" class=\"ui-btn ui-corner-all\">Edit Statuses</a>\n";
print "<a href=\"http://www.c2c-hit.net/c2cmobile/task/edittag.cgi\" target=\"_blank\" class=\"ui-btn ui-corner-all\">Edit Tags</a>\n";
}
print "</div>\n";

print "<h1>My Items</h1>";
if ($userrights > 1)
{
    print "<form method=\"post\">\n";
    if  ($listtype)
    {
	print selectList({
	    blankoption => 0,
	    multiple => 0,
	    options => {0 => "Detail", 1 => "Limited", 2 => "Simple"},
	    selected => [$listtype],
	    name => "listtype",
	    label => "List Types",
			 });
    }else
    {
	print selectList({
	    blankoption => 0,
	    multiple => 0,
	    options => {0 => "Detail", 1 => "Limited", 2 => "Simple"},
	    selected => [0],
	    name => "listtype",
	    label => "List Types",
			 });
    }
    print "<input type=\"submit\" name=\"changelist\" value=\"Change List Type\">\n";

    print "</form>\n";
}
if ($userrights > 1 && !$listtype)
{
    print "<form method=\"post\">\n";
    print "<input type=\"hidden\" name=\"myquery\" value=\"$query\">\n";    
}
if ($listtype == 2)
{
    print "<ul>\n";
    foreach my $item (@{$itemlist->[0]})
    {
	print "<li><a href=\"http://www.c2c-hit.net/c2cmobile/task/item.cgi?itemid=$item->{'itemid'}\" target=\"_blank\">$item->{'name'}</a></li>\n";
    }
    print "</ul>\n";
}else
{
    foreach my $item (@{$itemlist->[0]})
    {
	if ($listtype == 1)
	{
	    print itemDisplay($item, 1);
	}else
	{
	    print itemDisplay($item, $userrights);
	}
    }
}
print "<br>\n";
if ($userrights > 1 && !$listtype)
{
    print "<input type=\"submit\" name=\"update\" value=\"Update All\">\n";
}
print "</form>\n";


print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


