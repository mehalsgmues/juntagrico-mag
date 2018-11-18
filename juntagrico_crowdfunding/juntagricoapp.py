from juntagrico_crowdfunding.admin import *

def admin_menu_template():
    return ['cf/crowdfunding_admin_menu.html']
    
def fundable_inlines():
    return [FundableInline]
    
def fund_inlines():
    return [FundInline]
