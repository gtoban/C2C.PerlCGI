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
my $message;
my $hold;
my $groupid;
my $itemid;


#test form values and untaint

if ($cgi->param('groupid'))
{
    $groupid = $cgi->param('groupid');
}

if ($cgi->param('itemid'))
{
    $itemid = $cgi->param('itemid');
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
print jqpageheader("C2C Item Search", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

#if rights >= 1
#(
#name contains
#description contains
#tag =ANY in list
#status =ANY in list
#<=createdate
#>=createdate
#<=lasteditdate
#>=lasteditdate
#)if rights >= 2
#(
#type =ANY in list
#client
#<=startdate
#>=startdate
#<=enddate
#>=endate
#groupname contains (owned/associated)
#groupdescription contains (owned/associated)
#note/log contains
#)
#associated users (assigned)
#owner
print "<form method=\"POST\" action=\"http://www.c2c-hit.net/c2cmobile/task/itemsearchresult.cgi\" target=\"_blank\">\n";

#
#-----------------------HIDDEN ITEMS
#

if ($groupid)
{
    print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
}

if ($itemid)
{
    print "<input type=\"hidden\" name=\"itemid\" value=\"$itemid\">\n";
}


#
#------------------AND OR AND DEFAULT QUERY
#
my $ANDOR = {AND => "meet ALL criteria", OR => "meet ANY criteria"};
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print "<br/>\n";
print selectList({
    blankoption => 0,
    multiple => 0,
    options => $ANDOR,
    name => "andor",
    label => "ALL or ANY",
		 });
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print "<p>My Items Search</p>\n";
print checkbox([["myitemsearch", "Make This 'My Items' Search", 0, 0]]);
print "</div>\n";
print "</div>\n";

#
#------------------ITEM NAME AND DESCRIPTION
#
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print textInput({name => "itemname", label => "Item Name", value => ""});
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print textInput({name => "itemdescription", label => "Item Description", value => ""});
print "</div>\n";
print "</div>\n";

#
#-------------------TAGS
#
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
$hold = getAnySort(["SELECT * FROM itemtag WHERE tagdefault = 0", 0 ,0 ,0]);
my %tags;
foreach my $tag (@{$hold->[0]})
{
    $tags{$tag->{'id'}} = $tag->{'name'};
}
print selectList({
    blankoption => 1,
    multiple => 1,
    options => \%tags,
    name => "tag",
    label => "Tags",
		 });

print "</div>\n";
print "<div class=\"ui-block-b\">\n";

#
#-------------------STATUSES
#

$hold = getAnySort(["SELECT * FROM itemstatus WHERE active = 1", 0 ,0 ,0]);
my %statuses;
foreach my $status (@{$hold->[0]})
{
    $statuses{$status->{'id'}} = $status->{'name'};
}
print selectList({
    blankoption => 1,
    multiple => 1,
    options => \%statuses,
    name => "status",
    label => "Status",
		 });
print "</div>\n";
print "</div>\n";
#
#-------------------CREATE DATE & LAST EDIT DATE
#
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print "<p>Create Date </p>\n";
print "<p>Greater Than </p>\n";
print datepicker("creategreat");
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print "<p>Last Edit Date </p>\n";
print "<p>Greater Than </p>\n";
print datepicker("lasteditgreat");

print "</div>\n";
print "<div class=\"ui-block-a\">\n";
print "<p>Less Than </p>\n";
print datepicker("createless");
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print "<p>Less Than </p>\n";
print datepicker("lasteditless");
print "</div>\n";
print "</div>\n";



if ($userrights > 1)
{
    print "<div class=\"ui-grid-a\">\n";
    print "<div class=\"ui-block-a\">\n";
    #
    #-------------------DEFAULT TAGS
    #
    $hold = getAnySort(["SELECT * FROM itemtag WHERE tagdefault = 1", 0 ,0 ,0]);
    undef %tags;
    foreach my $tag (@{$hold->[0]})
    {
	$tags{$tag->{'id'}} = $tag->{'name'};
    }
    print selectList({
	blankoption => 1,
	multiple => 1,
	options => \%tags,
	name => "type",
	label => "Type",
		     });
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    #
    #-------------------CLIENT
    #
    $hold = getAnySort(["SELECT * FROM clients", 0 ,0 ,0]);
    my %clients;
    foreach my $client (@{$hold->[0]})
    {
	$clients{$client->{'id'}} = $client->{'name'};
    }
    print selectList({
	blankoption => 1,
	multiple => 1,
	options => \%clients,
	name => "client",
	label => "Client",
		     });
    print "</div>\n";
    print "</div>\n";

    #
    #-------------------START DATE & END DATE
    #
    print "<div class=\"ui-grid-a\">\n";
    print "<div class=\"ui-block-a\">\n";
    print "<p>Start Date </p>\n";
    print "<p>Greater Than </p>\n";
    print datepicker("startgreat");
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print "<p>End Date </p>\n";
    print "<p>Greater Than </p>\n";
    print datepicker("endgreat");
    print "</div>\n";
    print "<div class=\"ui-block-a\">\n";
    print "<p>Less Than </p>\n";
    print datepicker("startless");   
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print "<p>Less Than </p>\n";
    print datepicker("endless");
    print "</div>\n";
    print "</div>\n";
    

    #
    #------------------Group NAME & Description
    #
    print "<div class=\"ui-grid-a\">\n";
    print "<div class=\"ui-block-a\">\n";
    print textInput({name => "groupname", label => "Group Name", value => ""});
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print textInput({name => "groupdescription", label => "Group Description", value => ""});
    print "</div>\n";
    print "</div>\n";
    
    #
    #------------------NOTES
    #
    print "<div class=\"ui-grid-a\">\n";
    print "<div class=\"ui-block-a\">\n";
    print textInput({name => "itemnote", label => "Item Note", value => ""});
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
}

my %users;
if ($userrights > 2)
{

    #
    #-------------------USERS
    #
    $hold = getAnySort(["SELECT * FROM users", 0 ,0 ,0]);
    
    foreach my $user (@{$hold->[0]})
    {
	$users{$user->{'id'}} = "$user->{'firstName'} $user->{'lastName'}";
    }
    print selectList({
	blankoption => 1,
	multiple => 1,
	options => \%users,
	name => "user",
	label => "Associated Users",
		     });
 
}
if ($userrights > 1)
{
    print "</div>\n";
    print "</div>\n";
}

if ($userrights > 2)
{

    #
    #-------------------OWNER
    #
    $hold = getAnySort(["SELECT * FROM users", 0 ,0 ,0]);
    undef %users;
    foreach my $user (@{$hold->[0]})
    {
	$users{$user->{'id'}} = "$user->{'firstName'} $user->{'lastName'}";
    }
    print selectList({
	blankoption => 1,
	multiple => 1,
	options => \%users,
	name => "owner",
	label => "Item Owner",
		     });
 
}


#
#
#                  ORDER BY
#
#

#if rights >= 1
#(
#name contains 1
#status =ANY in list 1
#>=createdate 
#<=lasteditdate
#)if rights >= 2
#(
#type =ANY in list 1
#client 1
#>=startdate 1
#>=endate 1
#)
#?owner?

print "<h1>Order By</h1>\n";

print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print "<p> Criteria </p>\n";
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print "<p> Direction </p>\n";
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print "<p> Sort Order </p>\n";
print "</div>\n";
print "</div>\n";


#
#--------------------- Item Name
#

print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print checkbox([['itemnamecheck', "Item Name", 1, 0]]);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "itemnamedir",
	label => "Item Name Direction",
	hiddenlabel => 1
		 });
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "itemnamesortorder",
	label => "Item Name Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		 });
print "</div>\n";
print "</div>\n";

#
#--------------------- Item Status
#

print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print checkbox([['itemstatuscheck', "Item Status", 1, 0]]);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print selectList({
    blankoption => 0,
    multiple => 0,
    options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
    name => "itemstatusdir",
    label => "Item Status Direction",
    hiddenlabel => 1
		 });
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print selectList({
    blankoption => 1,
    multiple => 0,
    options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
    name => "itemstatussortorder",
    label => "Item Status Sort Order",
    hiddenlabel => 1,
    sortbykeys => 1 
		 });
print "</div>\n";
print "</div>\n";

#
#--------------------- Create Date
#

print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print checkbox([['createdatecheck', "Create Date", 1, 0]]);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "createdatedir",
	label => "Create Date Direction",
	hiddenlabel => 1 
		 });
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "createdatesortorder",
	label => "Create Date Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		 });
print "</div>\n";
print "</div>\n";
#
#--------------------- Last Edit Date
#

print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print checkbox([['lasteditdatecheck', "Last Edit Date", 1, 0]]);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "lasteditdatedir",
	label => "Last Edit Date Direction",
	hiddenlabel => 1 
		 });
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "lasteditdatesortorder",
	label => "Last Edit Date Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		 });
print "</div>\n";
print "</div>\n";

if ($userrights >= 2)
{
    #
    #--------------------- Item Type
    #

    print "<div class=\"ui-grid-b\">\n";
    print "<div class=\"ui-block-a\">\n";
    print checkbox([['typecheck', "Type", 1, 0]]);
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "typedir",
	label => "Type Direction",
	hiddenlabel => 1 
		     });
    print "</div>\n";
    print "<div class=\"ui-block-c\">\n";
    print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "typesortorder",
	label => "Type Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		     });
    print "</div>\n";
    print "</div>\n";
    #
    #--------------------- Item Client
    #

    print "<div class=\"ui-grid-b\">\n";
    print "<div class=\"ui-block-a\">\n";
    print checkbox([['clientcheck', "Client", 1, 0]]);
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "clientdir",
	label => "Client Direction",
	hiddenlabel => 1 
		     });
    print "</div>\n";
    print "<div class=\"ui-block-c\">\n";
    print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "clientsortorder",
	label => "Client Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		     });
    print "</div>\n";
    print "</div>\n";
    #
    #--------------------- Item StartDate
    #

    print "<div class=\"ui-grid-b\">\n";
    print "<div class=\"ui-block-a\">\n";
    print checkbox([['startdatecheck', "Start Date", 1, 0]]);
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "startdatedir",
	label => "Start Date Direction",
	hiddenlabel => 1 
		     });
    print "</div>\n";
    print "<div class=\"ui-block-c\">\n";
    print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "startdatesortorder",
	label => "Start Date Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		     });
    print "</div>\n";
    print "</div>\n";
    #
    #--------------------- Item EndDate
    #

    print "<div class=\"ui-grid-b\">\n";
    print "<div class=\"ui-block-a\">\n";
    print checkbox([['enddatecheck', "End Date", 1, 0]]);
    print "</div>\n";
    print "<div class=\"ui-block-b\">\n";
    print selectList({
	blankoption => 0,
	multiple => 0,
	options => {'DESC' => 'Desc', 'ASC' => 'Asc'},
	name => "enddatedir",
	label => "End Date Direction",
	hiddenlabel => 1 
		     });
    print "</div>\n";
    print "<div class=\"ui-block-c\">\n";
    print selectList({
	blankoption => 1,
	multiple => 0,
	options => {1 => 1, 2 => 2, 3 => 3, 4 =>4, 5 => 5, 6 => 6, 7 => 7, 8 => 8},
	name => "enddatesortorder",
	label => "End Date Sort Order",
	hiddenlabel => 1,
	sortbykeys => 1 
		     });
    print "</div>\n";
    print "</div>\n";

}

print "<input type=\"submit\" name=\"submit\" value=\"Search\">\n";

print "</form>\n";
print "</div>\n";


if ($message)
{
    print "<script> alert(\"$message\")</script>";
}

print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


