from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import cStringIO
import csv
import base64


class ImportInventoryWizard(osv.osv_memory):
    _name = 'import.inventory.wizard'
    _columns = {
	'name': fields.char('Name'),
	'location': fields.many2one('stock.location', 'Inventory Location'),
        'file': fields.binary('Input File'),
        'file_name': fields.char('File Name', size=64),
    }

    def import_inventory(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        file = wizard.file
        data = base64.decodestring(file)
        input = cStringIO.StringIO(data)
        reader = csv.DictReader(input, quotechar='"', delimiter=',')
        error_count = 0

	location = wizard.location.id
	name = wizard.name
	inventory_obj = self.pool.get('stock.inventory')
	v = {
	    'name': name,
	    'location_id': location,
	    'company_id': 1,
	    'state': 'draft',
	    'date': datetime.utcnow(),
	    'filter': 'partial',
	}
	inv_id = inventory_obj.create(cr, uid, v)

	line_obj = self.pool.get('stock.inventory.line')
        for row in reader:
	    sku = row['SKU']
	    qty = row['QTY']
	    product_id = self.find_product_id(cr, uid, sku)
	    if not product_id:
		print 'Product Not Found'
		continue

	    vals = {
		'inventory_id': inv_id,
		'location_id': location,
		'product_id': product_id,
		'product_uom_id': 1,
		'state': 'draft',
		'product_qty': qty,
	    }

	    line_id = line_obj.create(cr, uid, vals)

      #  datas = {'ids' : [inv_id]}
     #   datas['form'] = {}
#        return {
 #           'type': 'ir.actions.act_window',
  #          'report_name': 'stock.inventory',
   #         'datas' : datas,
    #    }
        inventory_obj.prepare_inventory(cr, uid, [inv_id])

    def find_product_id(self, cr, uid, sku):
	print 'SKU', sku
        product_obj = self.pool.get('product.product')
	product_ids = product_obj.search(cr, uid, [('default_code', '=', sku)])
	if product_ids:
	    return product_ids[0]

	return False
