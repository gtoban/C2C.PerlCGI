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
use itemDatabase qw(:Display :Item :Itemtag :Itemuser :Note :Groupitems :ItemToItem :Itemuserquery);

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
my $groupid;
my $itemid;
my %options;
my %selected;
my $first = 1;
my $firsti = 1;

my $itemlist;

my $ANDOR;
my $myitemsearch;

my $itemname;
my $itemdescription;
my @tags;
my @statuses;

my $yearcreategreat;
my $monthcreategreat;
my $daycreategreat;
my $datecreategreat;
my $yearcreateless;
my $monthcreateless;
my $daycreateless;
my $datecreateless;

my $yearlasteditgreat;
my $monthlasteditgreat;
my $daylasteditgreat;
my $datelasteditgreat;
my $yearlasteditless;
my $monthlasteditless;
my $daylasteditless;
my $datelasteditless;

my @types;
my @clients;

my $yearstartgreat;
my $monthstartgreat;
my $daystartgreat;
my $datestartgreat;
my $yearstartless;
my $monthstartless;
my $daystartless;
my $datestartless;

my $yearendgreat;
my $monthendgreat;
my $dayendgreat;
my $dateendgreat;
my $yearendless;
my $monthendless;
my $dayendless;
my $dateendless;

my $groupname;
my $groupdescription;
my $note;
my @users;
my @owners;

#ORDER BY VARS
my $count;
my @orderbyvars;

#UPDATE VAR
my $hold;
my $id;
my $update = $cgi->param('update');
my @updatesplit;
my $idlist;
my %params;
my @paramnames;
my $info;
my $tquery;

#test form values and untaint

if ($cgi->param('groupid'))
{
    $groupid = $cgi->param('groupid');
}

if ($cgi->param('itemid'))
{
    $itemid = $cgi->param('itemid');
}

if ($cgi->param('submit'))
{
    
    # QUERYBEGIN
    if ($userrights == 1)
    {
	$query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM (SELECT * FROM item ii WHERE ii.userid = $userid) i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
    }elsif ($userrights == 2)
    {
	if ($groupid)
	{
	    $query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM (SELECT * FROM item iii WHERE iii.id IN (SELECT ii.id FROM item ii WHERE ii.userid = $userid OR EXISTS (SELECT * FROM itemtouser iitu WHERE ii.id = iitu.itemid AND iitu.userid = $userid)) AND NOT EXISTS (SELECT * FROM groupitems giii WHERE giii.groupid = $groupid AND giii.itemid = iii.id)) i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
	}elsif ($itemid)
	{
	    $query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM (SELECT * FROM item iii WHERE iii.id IN (SELECT ii.id FROM item ii WHERE ii.userid = $userid OR EXISTS (SELECT * FROM itemtouser iitu WHERE ii.id = iitu.itemid AND iitu.userid = $userid)) AND NOT EXISTS (SELECT * FROM itemtoitem iiia WHERE iiia.aitemid = $itemid AND iiia.bitemid = iii.id UNION SELECT * FROM itemtoitem iiib WHERE iiib.bitemid = $itemid AND iiib.aitemid = iii.id )) i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
	}else
	{
	    $query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM (SELECT * FROM item ii WHERE ii.userid = $userid OR EXISTS (SELECT * FROM itemtouser iitu WHERE ii.id = iitu.itemid AND iitu.userid = $userid)) i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
	}
    }elsif ($userrights == 3)
    {
	if ($groupid)
	{
	    $query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM (SELECT * FROM item iii WHERE NOT EXISTS (SELECT * FROM groupitems giii WHERE giii.groupid = $groupid AND giii.itemid = iii.id)) i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
	}elsif ($itemid)
	{
	    $query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM (SELECT * FROM item iii WHERE NOT EXISTS (SELECT * FROM itemtoitem iiia WHERE iiia.aitemid = $itemid AND iiia.bitemid = iii.id UNION SELECT * FROM itemtoitem iiib WHERE iiib.bitemid = $itemid AND iiib.aitemid = iii.id )) i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
	}else
	{
	    $query = "SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM item i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id ";
	}
    }
    $ANDOR = $cgi->param('andor');
    $myitemsearch = $cgi->param('myitemsearch');

    $itemname = $cgi->param('itemname');
    $itemdescription = $cgi->param('itemdescription');
    @tags = $cgi->param('tag');
    @statuses = $cgi->param('status');
    
    $yearcreategreat = $cgi->param('yearcreategreat');   
    $monthcreategreat = $cgi->param('monthcreategreat');
    $daycreategreat = $cgi->param('daycreategreat');
    $yearcreateless = $cgi->param('yearcreateless');
    $monthcreateless = $cgi->param('monthcreateless');
    $daycreateless = $cgi->param('daycreategreat');

    $yearlasteditgreat = $cgi->param('yearlasteditgreat');   
    $monthlasteditgreat = $cgi->param('monthlasteditgreat');
    $daylasteditgreat = $cgi->param('daylasteditgreat');
    $yearlasteditless = $cgi->param('yearlasteditless');
    $monthlasteditless = $cgi->param('monthlasteditless');
    $daylasteditless = $cgi->param('daylasteditgreat');    
    
    @types = $cgi->param('type');
    @clients = $cgi->param('client');

    $yearstartgreat = $cgi->param('yearstartgreat');   
    $monthstartgreat = $cgi->param('monthstartgreat');
    $daystartgreat = $cgi->param('daystartgreat');
    $yearstartless = $cgi->param('yearstartless');
    $monthstartless = $cgi->param('monthstartless');
    $daystartless = $cgi->param('daystartgreat');

    $yearendgreat = $cgi->param('yearendgreat');   
    $monthendgreat = $cgi->param('monthendgreat');
    $dayendgreat = $cgi->param('dayendgreat');
    $yearendless = $cgi->param('yearendless');
    $monthendless = $cgi->param('monthendless');
    $dayendless = $cgi->param('dayendgreat');

    
    $groupname = $cgi->param('groupname');
    $groupdescription = $cgi->param('groupdescription');
    $note = $cgi->param('itemnote');
    @users = $cgi->param('user');

    #ORDER BY PARAMS

    $count = 0;
    if ($cgi->param('itemnamecheck'))
    {
	$orderbyvars[$count]->[0] = "i.name";
	$orderbyvars[$count]->[1] = $cgi->param('itemnamedir');
	$orderbyvars[$count]->[2] = $cgi->param('itemnamesortorder');
	$count += 1;
    }
    
    if ($cgi->param('itemstatuscheck'))
    {
	$orderbyvars[$count]->[0] = "iis.name";
	$orderbyvars[$count]->[1] = $cgi->param('itemstatusdir');
	$orderbyvars[$count]->[2] = $cgi->param('itemstatussortorder');
	$count += 1;
    }

    if ($cgi->param('createdatecheck'))
    {
	$orderbyvars[$count]->[0] = "i.createdate";
	$orderbyvars[$count]->[1] = $cgi->param('createdatedir');
	$orderbyvars[$count]->[2] = $cgi->param('createdatesortorder');
	$count += 1;
    }
    
    if ($cgi->param('lasteditdatecheck'))
    {
	$orderbyvars[$count]->[0] = "i.lasteditdate";
	$orderbyvars[$count]->[1] = $cgi->param('lasteditdatedir');
	$orderbyvars[$count]->[2] = $cgi->param('lasteditdatesortorder');
	$count += 1;
    }
    
    if ($cgi->param('typecheck'))
    {
	$orderbyvars[$count]->[0] = "ig.name";
	$orderbyvars[$count]->[1] = $cgi->param('typedir');
	$orderbyvars[$count]->[2] = $cgi->param('typesortorder');
	$count += 1;
    }
    
    if ($cgi->param('clientcheck'))
    {
	$orderbyvars[$count]->[0] = "iic.name";
	$orderbyvars[$count]->[1] = $cgi->param('clientdir');
	$orderbyvars[$count]->[2] = $cgi->param('clientsortorder');
	$count += 1;
    }
    
    if ($cgi->param('startdatecheck'))
    {
	$orderbyvars[$count]->[0] = "i.startdate";
	$orderbyvars[$count]->[1] = $cgi->param('startdatedir');
	$orderbyvars[$count]->[2] = $cgi->param('startdatesortorder');
	$count += 1;
    }
    
    if ($cgi->param('enddatecheck'))
    {
	$orderbyvars[$count]->[0] = "i.enddate";
	$orderbyvars[$count]->[1] = $cgi->param('enddatedir');
	$orderbyvars[$count]->[2] = $cgi->param('enddatesortorder');
	$count += 1;
    }
    
    #$itemnamecheck = $cgi->param('itemnamecheck');
    #$itemnamedir = $cgi->param('itemnamedir');
    #$itemnamesortorder = $cgi->param('itemnamesortorder');
    #
    #
    #$itemstatuscheck = $cgi->param('itemstatuscheck');
    #$itemstatusdir = $cgi->param('itemstatusdir');
    #$itemstatussortorder = $cgi->param('itemstatussortorder');
    
    #$createdatecheck = $cgi->param('createdatecheck');
    #$createdatedir = $cgi->param('createdatedir');
    #$createdatesortorder = $cgi->param('createdatesortorder');
    #
    #$lasteditdatecheck = $cgi->param('lasteditdatecheck');
    #$lasteditdatedir = $cgi->param('lasteditdatedir');
    #$lasteditdatesortorder = $cgi->param('lasteditdatesortorder');
    #
    #$typecheck = $cgi->param('');
    #$typedir = $cgi->param('user');
    #$typesortorder = $cgi->param('user');
    #
    #$clientcheck = $cgi->param('user');
    #$clientdir = $cgi->param('user');
    #$clientsortorder = $cgi->param('user');
    #
    #$startdatecheck = $cgi->param('user');
    #$startdatedir = $cgi->param('user');
    #$startdatesortorder = $cgi->param('user');
    #
    #$enddatecheck = $cgi->param('user');
    #$enddatedir = $cgi->param('user');
    #$enddatesortorder = $cgi->param('user');   

    #
    #-----------ITEM NAME
    #

    if ($itemname)
    {
	if ($first)
	{
	    $query .= "WHERE i.name LIKE '%$itemname%' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.name LIKE '%$itemname%' ";
	}

    }

    #
    #-----------ITEM DESCRIPTION
    #

    if ($itemdescription)
    {
	if ($first)
	{
	    $query .= "WHERE i.description LIKE '%$itemdescription%' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.description LIKE '%$itemdescription%' ";
	}

    }

    #
    #-----------TAGS
    #
    $firsti = 1;
    if (@tags)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM itemtotag ittg WHERE i.id = ittg.itemid AND ittg.tagid in ("; 
	    foreach my $tag (@tags)
	    {
		if ($firsti)
		{
		    $query .= "$tag";
		    $firsti = 0;
		}else
		{
		    $query .= ", $tag";
		}
	    }
	    $query .= ")) ";
	    $first = 0;
	}else
	{
	    
	    $query .= "$ANDOR EXISTS (SELECT * FROM itemtotag ittg WHERE i.id = ittg.itemid AND ittg.tagid in ("; 
	    foreach my $tag (@tags)
	    {
		if ($firsti)
		{
		    $query .= "$tag";
		    $firsti = 0;
		}else
		{
		    $query .= ", $tag";
		}
	    }
	    $query .= ")) ";
	}

    }

    #
    #-----------ITEM STATUSES
    #
    
    $firsti = 1;
    if (@statuses)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM itemstatus itts WHERE i.statusid = itts.id AND itts.id in ("; 
	    foreach my $status (@statuses)
	    {
		if ($firsti)
		{
		    $query .= "$status";
		    $firsti = 0;
		}else
		{
		    $query .= ", $status";
		}
	    }
	    $query .= ")) ";
	    $first = 0;
	}else
	{
	    
	    $query .= "$ANDOR EXISTS (SELECT * FROM itemstatus itts WHERE i.statusid = itts.id AND itts.id in ("; 
	    foreach my $status (@statuses)
	    {
		if ($firsti)
		{
		    $query .= "$status";
		    $firsti = 0;
		}else
		{
		    $query .= ", $status";
		}
	    }
	    $query .= ")) ";
	}

    }

    #
    #-----------CREATE DATES
    #

    if ($yearcreategreat && $monthcreategreat && $daycreategreat)
    {
	$datecreategreat = "$yearcreategreat-$monthcreategreat-$daycreategreat";
	if ($first)
	{
	    $query .= "WHERE i.createdate >= '$datecreategreat' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.createdate >= '$datecreategreat' ";
	}
    }

    if ($yearcreateless && $monthcreateless && $daycreateless)
    {
	$datecreateless = "$yearcreateless-$monthcreateless-$daycreateless";
	if ($first)
	{
	    $query .= "WHERE i.createdate <= '$datecreateless' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.createdate <= '$datecreateless' ";
	}
    }

    #
    #-----------last edit DATES
    #

    if ($yearlasteditgreat && $monthlasteditgreat && $daylasteditgreat)
    {
	$datelasteditgreat = "$yearlasteditgreat-$monthlasteditgreat-$daylasteditgreat";
	if ($first)
	{
	    $query .= "WHERE i.lasteditdate >= '$datelasteditgreat' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.lasteditdate >= '$datelasteditgreat' ";
	}
    }

    if ($yearlasteditless && $monthlasteditless && $daylasteditless)
    {
	$datelasteditless = "$yearlasteditless-$monthlasteditless-$daylasteditless";
	if ($first)
	{
	    $query .= "WHERE i.lasteditdate <= '$datelasteditless' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.lasteditdate <= '$datelasteditless' ";
	}
    }

    #
    #-----------TAG DEFAULT
    #
    $firsti = 1;
    if (@types)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM itemtotag itttg WHERE i.id = itttg.itemid AND itttg.id in ("; 
	    foreach my $tag (@types)
	    {
		if ($firsti)
		{
		    $query .= "$tag";
		    $firsti = 0;
		}else
		{
		    $query .= ", $tag";
		}
	    }
	    $query .= ")) ";
	    $first = 0;
	}else
	{
	    
	    $query .= "$ANDOR EXISTS (SELECT * FROM itemtotag itttg WHERE i.id = itttg.itemid AND itttg.id in ("; 
	    foreach my $tag (@types)
	    {
		if ($firsti)
		{
		    $query .= "$tag";
		    $firsti = 0;
		}else
		{
		    $query .= ", $tag";
		}
	    }
	    $query .= ")) ";
	}

    }

    #
    #-----------CLIENTS
    #
    $firsti = 1;
    if (@clients)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM clients c WHERE i.clientid = c.id AND c.id in ("; 
	    foreach my $client (@clients)
	    {
		if ($firsti)
		{
		    $query .= "$client";
		    $firsti = 0;
		}else
		{
		    $query .= ", $client";
		}
	    }
	    $query .= ")) ";
	    $first = 0;
	}else
	{
	    
	    $query .= "$ANDOR EXISTS (SELECT * FROM clients c WHERE i.clientid = c.id AND c.id in ("; 
	    foreach my $client (@clients)
	    {
		if ($firsti)
		{
		    $query .= "$client";
		    $firsti = 0;
		}else
		{
		    $query .= ", $client";
		}
	    }
	    $query .= ")) ";
	}

    }

     #
    #-----------START DATES
    #

    if ($yearstartgreat && $monthstartgreat && $daystartgreat)
    {
	$datestartgreat = "$yearstartgreat-$monthstartgreat-$daystartgreat";
	if ($first)
	{
	    $query .= "WHERE i.startdate >= '$datestartgreat' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.startdate >= '$datestartgreat' ";
	}
    }

    if ($yearstartless && $monthstartless && $daystartless)
    {
	$datestartless = "$yearstartless-$monthstartless-$daystartless";
	if ($first)
	{
	    $query .= "WHERE i.startdate <= '$datestartless' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.startdate <= '$datestartless' ";
	}
    }

     #
    #-----------END DATES
    #

    if ($yearendgreat && $monthendgreat && $dayendgreat)
    {
	$dateendgreat = "$yearendgreat-$monthendgreat-$dayendgreat";
	if ($first)
	{
	    $query .= "WHERE i.enddate >= '$dateendgreat' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.enddate >= '$dateendgreat' ";
	}
    }

    if ($yearendless && $monthendless && $dayendless)
    {
	$dateendless = "$yearendless-$monthendless-$dayendless";
	if ($first)
	{
	    $query .= "WHERE i.enddate <= '$dateendless' ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR i.enddate <= '$dateendless' ";
	}
    }

    #
    #-----------GROUP NAME
    #

    if ($groupname)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM itemgroups igps WHERE i.id = igps.itemid AND igps.name LIKE '%$groupname%') ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR EXISTS (SELECT * FROM itemgroups igps WHERE i.id = igps.itemid AND igps.name LIKE '%$groupname%') ";
	}

    }

    #
    #-----------GROUP DESCRIPTION
    #

    if ($groupdescription)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM itemgroups itgps WHERE i.id = itgps.itemid AND itgps.description LIKE '%$groupdescription%') ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR EXISTS (SELECT * FROM itemgroups itgps WHERE i.id = itgps.itemid AND itgps.description LIKE '%$groupdescription%') ";
	}

    }

    #
    #-----------NOTES
    #

    if ($note)
    {
	if ($first)
	{
	    $query .= "WHERE EXISTS (SELECT * FROM itemnote itmn WHERE i.id = itmn.itemid AND itmn.note LIKE '%$note%') ";
	    $first = 0;
	}else
	{
	    $query .= "$ANDOR EXISTS (SELECT * FROM itemnote itmn WHERE i.id = itmn.itemid AND itmn.note LIKE '%$note%') ";
	}

    }

    #
    #-----------USERS
    #
    $firsti = 1;
    my $userlist;
    if (@users)
    {
	if ($first)
	{
	    $userlist = "(";
	    foreach my $user (@users)
	    {
		if ($firsti)
		{
		    $userlist .= "$user";
		    $firsti = 0;
		}else
		{
		    $userlist .= ", $user";
		}
	    }
	    $userlist .= ")";
	    $query .= " WHERE EXISTS (SELECT * FROM itemtouser itu WHERE i.id = itu.itemid AND itu.userid in $userlist) ";
	    $first = 0;
	}else
	{	    
	    $userlist = "(";
	    foreach my $user (@users)
	    {
		if ($firsti)
		{
		    $userlist .= "$user";
		    $firsti = 0;
		}else
		{
		    $userlist .= ", $user";
		}
	    }
	    $userlist .= ")";
	    $query .= " $ANDOR EXISTS (SELECT * FROM itemtouser itu WHERE i.id = itu.itemid AND itu.userid in $userlist) ";
	}

    }

    #
    #-------------ORDER BY VARS
    #
    #$count = 0;
    #if ($itemnamecheck)
    #{
    #	$orderbyvars[$count]->[0] = "i.name";
    #	$orderbyvars[$count]->[1] = $itemstatusdir;
    #	$orderbyvars[$count]->[2] = $itemnamesortorder;
    #	$count += 1;
    #}
    #
    #
    #if ($itemstatuscheck)
    #{
    #	$orderbyvars[$count]->[0] = "iis.name";
    #	$orderbyvars[$count]->[1] = $itemstatusdir;
    #	$orderbyvars[$count]->[2] = $itemstatussortorder;
    #	$count += 1;
    #}
    $first = 1;
    foreach my $sort (sort { $a->[2] <=> $b->[2] } @orderbyvars)
    {
	if ($first)
	{
	    $query .= " ORDER BY $sort->[0] $sort->[1]";
	    $first = 0;
	}else
	{
	     $query .= ", $sort->[0] $sort->[1]";
	}
    }

    if ($myitemsearch)
    {
	$hold = itemUserQuery($userid, $userrights, $query);
    }

    $itemlist = getAnySort([$query, 0, 0, 0]);    
    
}elsif ($update)
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

    $itemlist = getAnySort([$query, 0, 0, 0]); 
     
}elsif ($cgi->param('addtogroup'))
{
    #@paramnames = $cgi->param;
    $groupid = $cgi->param('groupid');
    $query = $cgi->param('myquery');
    $itemlist = getAnySort([$query, 0, 0, 0]);
    my $test;
    $count = 0;
    foreach my $item (@{$itemlist->[0]})
    {
	$test = "$item->{'itemid'}.check";
	if ($cgi->param("$test"))
	{
	    $idlist->[$count] = $item->{'itemid'};
    	    $count += 1;
	}
	
    }
    if ($idlist)
    {
    	$hold = addEditGroupItems([$userid, $groupid, $idlist]);
    }    
    
}elsif ($cgi->param('addtoitem'))
{
    $itemid = $cgi->param('itemid');
    $query = $cgi->param('myquery');
    $itemlist = getAnySort([$query, 0, 0, 0]);
    my $test;
    $count = 0;
    foreach my $item (@{$itemlist->[0]})
    {
	$test = "$item->{'itemid'}.check";
	if ($cgi->param("$test"))
	{
	    $idlist->[$count] = $item->{'itemid'};
    	    $count += 1;
	}
	
    }
    if ($idlist)
    {
	$hold = addItemToItem([$userid, $itemid, $idlist]);
    }
    
    $itemlist = getAnySort([$query, 0, 0, 0]);
}

if (!$itemlist->[1])
{
    $message .= "ERROR: $itemlist->[2] : $itemlist->[3]";
}




#HTML with FORM

print $cgi->header();
my $javascript = "<script>\n";
$javascript .= "function confirmDelete() {\n";
$javascript .= "return confirm('Are you sure you want to delete this?');\n";
$javascript .= "}\n";
$javascript .= "</script>\n";
print jqheader($javascript);

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Item Search Results", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";
if ($itemlist->[1])
{
    #print $query;
    print "<h3> Results </h3>\n";
    #print "TEST:: $itemlist->[0][0]{'client'} :: $itemlist->[2] : $itemlist->[3]";
    print "<form method=\"post\">\n";
    print "<input type=\"hidden\" name=\"myquery\" value=\"$query\">\n";
    if ($itemid)
    {
	print "<input type=\"hidden\" name=\"itemid\" value=\"$itemid\">\n";
    }elsif ($groupid)
    {
	print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
    }
    my $notadded;
    foreach my $item (@{$itemlist->[0]})
    {
	#print "ITEMID::  $item->{'itemid'}\n";
	$notadded = 1;
	if ($groupid || $itemid)
	{
	    foreach my $id (@{$idlist})
	    {
		if ($id == $item->{'itemid'})
		{
		    $notadded = 0;
		}
	    }
	    if ($notadded)
	    {
		print itemDisplay($item, $userrights, 1);
	    }
	}else
	{
	    print itemDisplay($item, $userrights); #item, editable, group
	}
    }
    print "<br>\n";
    if ($userrights < 2 || $itemid || $groupid)
    {
	if ($itemid)
	{
	    print "<input type=\"submit\" name=\"addtoitem\" value=\"Add To Item\">\n";
	}elsif ($groupid)
	{
	    print "<input type=\"submit\" name=\"addtogroup\" value=\"Add To Group\">\n";
	}
    }else
    {
	print "<input type=\"submit\" name=\"update\" value=\"Update All\">\n";
    }
    print "</form>\n";
    
}else
{
    print $message;
}

# CLIENTS CAN NOT EDIT!!!
# Click to view (hyperlink with Click to view)
# if (userrights > 1)
# (type) YOU GET LINK WITH TAG OR JUST LINK
# itemname
# itemdescription
# tags
# status
# place to add note
# list of owned group hyperlinks??
# list of member of group hyperlinks??
#if (>1 and owner/associated or admin) edit button for each and at end


print "</div>\n";

if ($message)
{
    print "<script> alert(\"$message\")</script>";
}


print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();

sub myowner
{
    my $titemid = shift;
    my $assigned = getAnySort(["SELECT * FROM itemtouser WHERE itemid = $titemid AND userid = $userid UNION SELECT * FROM item WHERE id = $titemid AND userid = $userid", 0, 0, 0]);
    if ($assigned->[0][0] && $userrights >= 2)
    {
	return 1;
    }elsif ($userrights == 3)
    {
	return 1;
    }

    return 0;
}


