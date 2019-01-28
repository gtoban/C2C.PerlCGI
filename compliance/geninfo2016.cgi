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



#test form values and untaint

#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C MU 2016", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

print "<h1 align=\"center\">How To MU in 2016 - Cheat Sheet</h1>\n";
print "<h2 align=\"center\">Reporting Period is the full year, January 1 - December 31, 2016</h2> \n";

print "<ol>\n";
print "<li><h3>Protect a Patient Health Information: </h3></li>\n";
print "<p> Conduct or review a security risk analysis. (Your IT company can do this.)</p>\n";

print "<li><h3>Clinical Decision Support:</h3></li>\n";
print "<ol type=\"a\">\n";
print "<li>Implement 5 clinical decision support rules. (1-time setup but may be changed at any time if you'd like other alerts implemented.)</li>\n";
print "<li>Enable and implement durg-drug and drug allergy interactions. (This is set up in User Settings Admin. 1-time setup.)</li>\n";
print "</ol>\n";

print "<li><h3>Computerized Provider Order Entry:</h3></li>\n";
print "<ol type=\"a\">\n";
print "<li>Medication orders</li>\n";
print "<li>Lab Orders</li>\n";
print "<li>Radiology orders must be created in PrimeSuite. If you are using th e plan section of your note for orders and medications then you are in compliance.</li>\n";
print "</ol>\n";

print "<li><h3>Electronic Prescribing:</h3></li>\n";
print "<p>use eRx for all permissible prescriptions and more than 50% of those permissible prescriptions are queried for a drug formulary. (If you have SureScripts, then 1-time setup of the automatic query in eRx Eligibility.)</p>\n";

print "<li><h3>Health Information Exchange:</h3></li>\n";
print "<ul type=\"square\">\n";
print "<li>Only when a patient is <strong>referred OUT</strong>, check <strong>care transition</strong>.</li>\n";
print "<li>If a summary of care was sent (via any method), check <strong>summary of care provided</strong>.</li>\n";
print "<li>If an <strong>ambulatory summary</strong> was sent to via <strong>Updox</strong>, check <strong>summary of care direct</strong>. (This must be done on >10/% of outbound referrals.)</li>\n";
print "<li>You are <strong>exempt if</strong> you refer out fewer than 100 times during the reporting period.</li>\n";
print "</ul>\n";

print "<li><h3>Patient Specific Education:</h3></li>\n";
print "<p>check the box for <strong>Patient Specific Education Materials Provided</strong> when patient specific education resources identified by CEHRT are provided to the patient. (May use the green i - info buttons on the Facesheet for patient specific education materials.)</p>\n";

print "<li><h3>Medication Reconciliation:</h3></li>\n";
print "<p>for all <strong>new patients and inbound referrals</strong> check the 2 boxes - <strong>Transition of Care</strong> (to indicate inbound referral) and <strong>Medications Have Been Reconciled</strong> (to indicate that the meds have been reconciled) </p>\n";

print "<li><h3>Patient Electronic Access (VDT):</h3></li>\n";
print "<ol type=\"a\">\n";
print "<li>50/% of all unique patients must be <strong>provided timely access</strong> to their medical info via the patietn portal. (Get MU credit by ensuring that the <strong>Patient Portal Invite</strong> flag is assigned to the patient.)</li>\n";
print "<li>At least <strong> 1 patient</strong> must view/download/transmit his/her health info on the patient portal during the reporting peroiod.</li>\n";
print "</ol>\n";

print "<li><h3>Secure Messaging:</h3></li>\n";
print "<p>must have the <strong>capability</strong> for patients to send and receive a secure electronic message. If you have a Patient Portal then you have this functionality.</p>\n";

print "<li><h3>Clinical Decision Support:</h3></li>\n";
print "<ol type=\"a\">\n";
print "<li>Immunization Registry</li>\n";
print "<li>Syndromic Surveillance</li>\n";
print "<li>Specialized Registry Reporting</li>\n";
print "</ol>\n";
print "</ol>\n";


print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


