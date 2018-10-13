
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import BaseUserManager
from datetime import datetime



class AfUsuario(models.Model):

    #id = models.AutoField(primary_key=True)
    #id                  = models.IntegerField(primary_key=True, editable=False, auto_created=True, db_column='id')
    user                = models.OneToOneField(User,unique=True, on_delete=models.CASCADE)
    usu_administrador   = models.BooleanField(default=False,verbose_name='Usuario administrador afcloud')

    def setUser(self,usuario):
        self.user= usuario


    def setAFC_Administrador(self,adm):
        self.usu_administrador=adm


    def save(self,*args,**kwargs):
        if not self.user.first_name:
            raise ValueError('El nombre de usuario es un campo obligatorio')
        if not self.user.password:
            raise ValueError ('Contraseña es obligatoria')

        u = super(AfUsuario, self).save(*args, **kwargs)
        #AfUsuario.objects.create_user(user=u )

    def __str__(self):
        #return str(id)
        return str(self.user.username.encode('utf-8', 'ignore'))

    class Meta:
        managed = True
        db_table = 'af_usuario'




class AfAuditoria(models.Model):
    #aud_id = models.AutoField(primary_key=True)
    #id               = models.IntegerField(primary_key=True, editable=False, auto_created=True, db_column='id')
    aud_entidad_id   = models.IntegerField()
    aud_entidad_tipo = models.CharField(max_length=100)
    usu_username     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='afauditorias')
    aud_detalle_pre  = models.CharField(max_length=250, blank=True, null=True)
    aud_detalle_pos  = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return '%s %s %s' % (self.usu_username, self.aud_detalle_pre, self.aud_detalle_pos)


    class Meta:
        managed = True
        #db_table = 'AF_AUDITORIA'
        db_table = 'af_auditoria'

class AfServicio(models.Model):
    #ser_id = models.AutoField(primary_key=True)
    #id               = models.IntegerField(primary_key=True, editable=False, auto_created=True, db_column='id')
    ser_nombre       = models.CharField(max_length=100, verbose_name="Nombre del servicio")
    ser_descripcion  = models.CharField(max_length=250, verbose_name="Descripción",blank=True, null=True)
    ser_tarifa       = models.DecimalField(max_digits=10, verbose_name="Tarifa", decimal_places=2, blank=True, null=True)
    ser_activo       = models.BooleanField(default=1, verbose_name='Activo')

    def __str__(self):
        return str(self.ser_nombre.encode('utf-8', 'ignore'))


    class Meta:
        managed = True
        #db_table = 'AF_SERVICIO'
        db_table = 'af_servicio'



class AfEntorno(models.Model):
    #ent_id = models.AutoField(primary_key=True)
    #id              = models.IntegerField(primary_key=True, editable=False, auto_created=True, db_column='id')
    ent_nombre      = models.CharField(max_length=100,verbose_name="Nombre del entorno", blank=False)
    ent_descripcion = models.CharField(max_length=250, verbose_name="Descripción del entorno",blank=True, null=True)
    ent_uri         = models.URLField(max_length=100, verbose_name="URI",blank=True,null=True)
    ent_username    = models.CharField(max_length=50, verbose_name="Username", blank=True, null=True)
    ent_password    = models.CharField(max_length=250, blank=True, verbose_name="Password", null=True)
    ent_activo      = models.BooleanField(default=1, verbose_name='Activo')
    ent_config_file = models.FileField( blank=True,verbose_name="Fichero de entorno")

    num_proyectos   = 0
    proyectos_list =[]
    proyectos_list_str=''

    def set_num_proyectos(self, n):
        self.num_proyectos=n

    def get_num_proyectos(self):
        return self.num_proyectos

    def get_proyectos_str(self):
        return ','.join(self.proyectos_list)

    def __str__(self):
        return '%s ' % (self.ent_nombre)
        #return str(self.ent_nombre.encode('utf-8', 'ignore'))


    @classmethod
    def create(cls, nombre, descripcion, uri, usuario, password, activo):
        entorno = cls(ent_nombre=nombre, ent_descripcion=descripcion, ent_uri=uri,ent_username=usuario, ent_password=password, ent_activo=activo )
        return entorno


    class Meta:
        managed = True
        db_table = 'af_entorno'


class AfProyecto(models.Model):

    pro_nombre       = models.CharField(max_length=100,verbose_name='Nombre',unique=True)
    pro_descripcion  = models.CharField(max_length=250,verbose_name='Descripción', blank=True, null=True)
    pro_activo       = models.BooleanField(default=1, verbose_name='Activo')
    num_integrantes  = 0
    num_entornos     = 0
    entornos=[]
    integrantes_lst= []
    entornos_lst   = []
    integrantes_str=''
    entornos_str=''

    def setEntornos(self,ents):
        self.entornos=ents


    def __str__(self):
        return str(self.pro_nombre.encode('utf-8', 'ignore'))

    @classmethod
    def create(cls, nombre, descripcion, activo):
        proyecto = cls(pro_nombre=nombre, pro_descripcion=descripcion, pro_activo=activo)
        return proyecto


    def set_num_integrantes(self, n):
        self.num_integrantes=n

    def get_num_integrantes(self):
        return len(self.integrantes_lst)

    def set_num_entornos(self, n):
        self.num_entornos=n

    def get_num_entornos(self):
        return len(self.entornos)

    def set_integrantes(self,integrantes):
        self.integrantes_lst=integrantes

    def set_entornos(self, entornos):
        self.entornos_lst=entornos

    def get_entornos_str(self):
        return ','.join(self.entornos_lst)

    def get_integrantes_str(self):
        return ','.join(self.integrantes_lst)

    class Meta:
        managed = True
        db_table = 'af_proyecto'



    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)  # Call the "real" save() method.
        #do_something_else()


class AfRelEntPro(models.Model):

    ent          = models.ForeignKey(AfEntorno, on_delete=models.CASCADE)
    pro          = models.ForeignKey(AfProyecto, on_delete=models.CASCADE)
    rep_activo   = models.BooleanField(default=1, verbose_name='Activo')

    def __str__(self):
        return '%s %s' % (self.ent.ent_nombre, self.pro.pro_nombre)

    class Meta:
        managed = True
        db_table = 'af_rel_ent_pro'
        db_tablespace = 'af_entorno', 'af_proyecto'

    @classmethod
    def create(cls, entorno, proyecto ):
        rel_ent_pro = cls(ent=entorno, pro=proyecto)
        return rel_ent_pro




class AfLineaCatalogo(models.Model):

    pro                 = models.ForeignKey(AfProyecto, on_delete=models.CASCADE)
    ser                 = models.OneToOneField(AfServicio, on_delete=models.CASCADE)
    lca_tarifa          = models.FloatField(blank=True, null=True)
    lca_configuracion   = models.CharField(max_length=250, blank=True, null=True)
    lca_activo          = models.BooleanField(default=1, verbose_name='Activo')

    def __str__(self):
        return '%s %s' % (self.pro.pro_nombre, self.ser.ser_nombre)

    class Meta:
        managed = True
        db_table = 'af_linea_catalogo'
        db_tablespace = 'af_servicio', 'af_proyecto'

class AfInstancia(models.Model):

    lca          = models.ForeignKey(AfLineaCatalogo,  on_delete=models.CASCADE)
    rep          = models.ForeignKey(AfRelEntPro,  on_delete=models.CASCADE)
    ins_kubeid   = models.CharField(max_length=100)
    ins_uri      = models.CharField(max_length=100, blank=True, null=True)
    ins_activo   = models.BooleanField(default=1, verbose_name='Activo')

    def __str__(self):
        return 'lc_id: %s %s %s' % (self.lca.id, self.lca.ser.ser_nombre, self.rep.ent.ent_nombre)

    class Meta:
        managed = True
        db_table = 'af_instancia'
        db_tablespace = 'af_linea_catalogo'



class AfCiclo(models.Model):

    ins              = models.ForeignKey(AfInstancia, default='', on_delete=models.CASCADE, related_name='afciclos')
    cic_fecha_inicio = models.DateTimeField(default=datetime.now, blank=True)
    cic_fecha_fin    = models.DateTimeField(default=datetime.now, blank=True)


    def __str__(self):
        return '%s %s %s' % (self.ins.id, self.cic_fecha_inicio, self.cic_fecha_fin)

    class Meta:
        managed = True
        db_table = 'af_ciclo'
        db_tablespace = 'af_instancia'


class AfTipoPerfil(models.Model):

    tpe_nombre      = models.CharField(max_length=100)
    tpe_descripcion = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return str(self.tpe_nombre.encode('utf-8', 'ignore'))

    class Meta:
        managed = True
        db_table = 'af_tipo_perfil'


class AfPerfil(models.Model):

    variable_interna=0
    usu = models.ForeignKey(AfUsuario,  on_delete=models.CASCADE)
    pro = models.ForeignKey(AfProyecto, on_delete=models.CASCADE)
    tpe = models.ForeignKey(AfTipoPerfil,  on_delete=models.CASCADE)
    per_activo = models.BooleanField(default=1, verbose_name='Activo')


    def __str__(self):
        return '%s %s %s' % (self.usu, self.pro.pro_nombre, self.tpe.tpe_nombre)


    def get_variable_interna(self):
        return self.variable_interna


    class Meta:
        managed = True
        db_table = 'af_perfil'
        db_tablespace = 'af_usuario', 'af_proyecto', 'af_tipo_perfil'
