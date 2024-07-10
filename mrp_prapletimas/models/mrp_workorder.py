from odoo import models, fields, api

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    sequence = fields.Integer()

    eiliskumas = []
    veiksmai = []
    perkelto_nr = None
    jau_perkelta = False

    @classmethod
    def pertempimas(cls, seqpries, seqpo, id, env):

        print(MrpWorkorder.eiliskumas)
        print(f"prieš įrašymą: {MrpWorkorder.veiksmai}")
        MrpWorkorder.veiksmai.append([seqpries, seqpo, id])
        print(f"po įrašymo: {MrpWorkorder.veiksmai}")

        if len(MrpWorkorder.veiksmai) == len(MrpWorkorder.eiliskumas[0]):
            MrpWorkorder.jau_perkelta = True

        if MrpWorkorder.jau_perkelta == False:
            suma = 0
            prideta = 0
            print(suma)
            for pakeitimas in MrpWorkorder.veiksmai:
                skirtumas = pakeitimas[0] - pakeitimas[1]
                if skirtumas != 0:
                    suma += skirtumas
                    prideta += 1

            if suma == 0 and prideta > 1:
                print(suma)
                MrpWorkorder.jau_perkelta = True
        if MrpWorkorder.jau_perkelta == True:
            for i, pakeitimas in enumerate(MrpWorkorder.veiksmai):

                if pakeitimas[0] < pakeitimas[1]:
                    pakeitimas.append('perkeltas')
                    MrpWorkorder.perkelto_nr = i
                elif pakeitimas[0] > pakeitimas[1] and pakeitimas[0] - pakeitimas[1] == 1:
                    pakeitimas.append('persistume')
                else:
                    pakeitimas.append('neaisku')

            for pakeitimas in MrpWorkorder.veiksmai:
                perkeltas = env['mrp.workorder'].browse(MrpWorkorder.veiksmai[MrpWorkorder.perkelto_nr][2])
                perkeltas.write({'state': 'progress'})
                if pakeitimas[3] == 'persistume' and pakeitimas[0] > MrpWorkorder.veiksmai[MrpWorkorder.perkelto_nr][0] and pakeitimas[1] < MrpWorkorder.veiksmai[MrpWorkorder.perkelto_nr][1]:
                    record = env['mrp.workorder'].browse(pakeitimas[2])
                    if record.production_id == perkeltas.production_id:
                        record.write({'state': 'done'})

        #     siuksliu surinkimas
        if MrpWorkorder.jau_perkelta == True:
            MrpWorkorder.eiliskumas.clear()
            MrpWorkorder.veiksmai.clear()
            MrpWorkorder.perkelto_nr = None
            MrpWorkorder.jau_perkelta = False

        print(MrpWorkorder.veiksmai)


    @api.model
    def write(self, vals):
        if 'sequence' in vals:
            seqpries = self.sequence
            seqpo = vals['sequence']
            center = self.workcenter_id.id
            domain = [('workcenter_id', '=', center)]
            if self.eiliskumas == []:

                self.eiliskumas.append(self.search(domain))

            self.pertempimas(seqpries, seqpo, self.id, self.env)
            print(self.search(domain))

            rez = super(MrpWorkorder, self).write(vals)
        else:
            rez = super(MrpWorkorder, self).write(vals)
        return rez

    @api.model
    def create(self, vals):
        if 'sequence' not in vals:
            highest = self.search([('workcenter_id', '=', vals['workcenter_id'])], order='sequence desc', limit=1).sequence
            vals['sequence'] = highest + 1 if highest is not None else 0
        return super(MrpWorkorder, self).create(vals)