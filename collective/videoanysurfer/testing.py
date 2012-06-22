from plone.testing import z2

from plone.app.testing import *
import collective.videoanysurfer

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.videoanysurfer,
                                additional_z2_products=[],
                                gs_profile_id='collective.videoanysurfer:default',
                                name="collective.videoanysurfer:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.videoanysurfer:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.videoanysurfer:Functional")

